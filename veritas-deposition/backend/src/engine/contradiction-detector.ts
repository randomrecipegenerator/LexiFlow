import { PrismaClient } from '@prisma/client';
import { analyzeContradiction, generateCrossExamQuestions, calculateCredibilityScore, ContradictionAnalysis } from './openai-client';
import { generateEmbedding, parseTranscriptIntoSegments, findSimilarSegments } from './embedding-service';

const prisma = new PrismaClient();

export interface DetectionResult {
  depositionId: string;
  contradictionsFound: number;
  contradictions: Array<{
    id: string;
    type: string;
    severity: string;
    testimonyA: string;
    testimonyB: string;
    reasoning: string;
    confidence: number;
  }>;
  credibilityScore: number;
  crossExamQuestions: Array<{
    severity: string;
    question: string;
    testimonyContext: string;
  }>;
  processingTimeMs: number;
}

/**
 * Main entry point: Run full contradiction detection on a deposition.
 *
 * Pipeline:
 * 1. Parse transcript → structured Testimony segments
 * 2. Generate embeddings for each segment (for RAG)
 * 3. INTERNAL detection: Compare each witness statement against others
 * 4. EVIDENCE detection: Compare testimony against uploaded evidence text
 * 5. Score confidence via OpenAI reasoning
 * 6. Generate cross-examination questions
 * 7. Calculate witness credibility score
 * 8. Persist all contradictions and analysis to database
 */
export async function detectContradictions(depositionId: string): Promise<DetectionResult> {
  const startTime = Date.now();

  // 1. Load deposition with testimony and evidence
  const deposition = await prisma.deposition.findUnique({
    where: { id: depositionId },
    include: {
      matter: {
        include: {
          evidence: { where: { filePath: { not: null } } },
        },
      },
      testimony: { orderBy: { order: 'asc' } },
    },
  });

  if (!deposition) {
    throw new Error(`Deposition not found: ${depositionId}`);
  }

  const transcriptText = deposition.transcriptText;
  const existingTestimony = deposition.testimony;
  const evidenceDocs = deposition.matter.evidence;

  // 2. If no structured testimony exists, parse the transcript
  let testimonySegments = existingTestimony;
  if (testimonySegments.length === 0 && transcriptText) {
    const parsed = parseTranscriptIntoSegments(transcriptText, depositionId);
    
    // Save parsed segments and generate embeddings
    for (const seg of parsed) {
      const embedding = await generateEmbedding(seg.text);
      const created = await prisma.testimony.create({
        data: {
          depositionId,
          text: seg.text,
          speaker: seg.speaker,
          pageNumber: seg.pageNumber,
          lineNumber: seg.lineNumber,
          order: seg.pageNumber ? (seg.pageNumber * 100 + (seg.lineNumber || 0)) : 0,
          embedding: embedding as any, // pgvector expects Float[]
        },
      });
      testimonySegments.push(created);
    }
  }

  const allContradictions: ContradictionAnalysis[] = [];

  // 3. INTERNAL contradiction detection (witness vs. own testimony)
  const witnessStatements = testimonySegments.filter(t => t.speaker === 'WITNESS');
  const witnessEmbeddings = await Promise.all(
    witnessStatements.map(s => generateEmbedding(s.text))
  );

  // Compare each witness statement against every other witness statement
  for (let i = 0; i < witnessStatements.length; i++) {
    for (let j = i + 1; j < witnessStatements.length; j++) {
      // Use semantic similarity to find potentially conflicting statements
      const similarity = cosineSimilarityApprox(
        witnessEmbeddings[i],
        witnessEmbeddings[j]
      );

      // Only analyze if statements are semantically related
      if (similarity > 0.65) {
        const result = await analyzeContradiction(
          witnessStatements[i].text,
          witnessStatements[j].text,
          deposition.witnessName || 'Witness',
          deposition.witnessName || 'Witness',
        );
        if (result) {
          result.type = 'INTERNAL';
          allContradictions.push(result);
        }
      }
    }
  }

  // 4. EVIDENCE contradiction detection (testimony vs. documentary evidence)
  for (const evidence of evidenceDocs) {
    if (!evidence.description && !evidence.filePath) continue;
    
    const evidenceText = evidence.description || `[Evidence: ${evidence.title}]`;
    const evidenceEmbedding = await generateEmbedding(evidenceText);

    for (let i = 0; i < witnessStatements.length; i++) {
      const similarity = cosineSimilarityApprox(
        evidenceEmbedding,
        witnessEmbeddings[i]
      );

      if (similarity > 0.7) {
        const result = await analyzeContradiction(
          witnessStatements[i].text,
          evidenceText,
          deposition.witnessName || 'Witness',
          `Evidence: ${evidence.title}`,
          undefined,
          `Evidence Type: ${evidence.evidenceType}`,
        );
        if (result) {
          result.type = 'EVIDENCE';
          result.evidenceTitle = evidence.title;
          allContradictions.push(result);
        }
      }
    }
  }

  // 5. Persist all detected contradictions to database
  const persistedContradictions = [];
  for (const c of allContradictions) {
    // Find matching testimony IDs in the database
    const testimonyMatchA = testimonySegments.find(t => t.text === c.testimonyA);
    const testimonyMatchB = testimonySegments.find(t => t.text === c.testimonyB);
    const evidenceMatch = c.evidenceTitle
      ? evidenceDocs.find(e => e.title === c.evidenceTitle)
      : null;

    const created = await prisma.contradiction.create({
      data: {
        matterId: deposition.matterId,
        depositionId,
        type: c.type as any,
        severity: c.severity as any,
        testimonyIdA: testimonyMatchA?.id || '',
        testimonyTextA: c.testimonyA,
        testimonyIdB: testimonyMatchB?.id || '',
        testimonyTextB: c.testimonyB,
        evidenceId: evidenceMatch?.id || undefined,
        reasoning: c.reasoning,
        confidence: c.confidence,
      },
    });
    persistedContradictions.push(created);
  }

  // 6. Generate cross-examination questions
  const crossExamQuestions = await generateCrossExamQuestions(
    allContradictions.filter(c => c.severity === 'HIGH' || c.severity === 'MEDIUM')
  );

  // 7. Calculate credibility score
  const highCount = allContradictions.filter(c => c.severity === 'HIGH').length;
  const mediumCount = allContradictions.filter(c => c.severity === 'MEDIUM').length;
  const credibilityScore = calculateCredibilityScore(
    allContradictions.length,
    highCount,
    mediumCount,
  );

  // 8. Persist AI analysis summary
  await prisma.aiAnalysis.upsert({
    where: { depositionId },
    update: {
      contradictions: allContradictions.length,
      keyAdmissions: allContradictions.filter(c => c.type === 'EVIDENCE').length,
      credibilityScore,
      summary: `Analysis complete: ${allContradictions.length} contradictions found (${highCount} high severity). Credibility score: ${credibilityScore}.`,
      analysisJson: JSON.stringify(allContradictions),
      modelVersion: process.env.OPENAI_MODEL || 'gpt-4o',
      processingTimeMs: Date.now() - startTime,
    },
    create: {
      depositionId,
      contradictions: allContradictions.length,
      keyAdmissions: allContradictions.filter(c => c.type === 'EVIDENCE').length,
      credibilityScore,
      summary: `Analysis complete: ${allContradictions.length} contradictions found.`,
      analysisJson: JSON.stringify(allContradictions),
      modelVersion: process.env.OPENAI_MODEL || 'gpt-4o',
      processingTimeMs: Date.now() - startTime,
    },
  });

  // Update deposition status and credibility score
  await prisma.deposition.update({
    where: { id: depositionId },
    data: {
      status: 'ANALYZED',
      aiProcessed: true,
      credibilityScore,
    },
  });

  return {
    depositionId,
    contradictionsFound: allContradictions.length,
    contradictions: allContradictions.map(c => ({
      id: '', // Will be populated after DB insert
      type: c.type,
      severity: c.severity,
      testimonyA: c.testimonyA,
      testimonyB: c.testimonyB,
      reasoning: c.reasoning,
      confidence: c.confidence,
    })),
    credibilityScore,
    crossExamQuestions,
    processingTimeMs: Date.now() - startTime,
  };
}

/**
 * Compute approximate cosine similarity between two embedding arrays.
 * Used pre-filter before calling OpenAI to save API costs.
 */
function cosineSimilarityApprox(a: number[], b: number[]): number {
  if (!a || !b || a.length !== b.length || a.length === 0) return 0;
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  if (na === 0 || nb === 0) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}