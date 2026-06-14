import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

export interface ContradictionAnalysis {
  type: 'INTERNAL' | 'EVIDENCE' | 'EXTERNAL' | 'IMPOSSIBILITY';
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  testimonyA: string;
  testimonyB: string;
  evidenceTitle?: string;
  reasoning: string;
  confidence: number;
  pageA?: number;
  pageB?: number;
}

export interface CrossExaminationQuestion {
  severity: string;
  question: string;
  testimonyContext: string;
}

/**
 * Analyze two testimony excerpts for contradictions using OpenAI.
 */
export async function analyzeContradiction(
  textA: string,
  textB: string,
  witnessNameA: string,
  witnessNameB: string,
  contextA?: string,
  contextB?: string,
): Promise<ContradictionAnalysis | null> {
  const prompt = `You are Veritas™, a legal AI specializing in deposition contradiction detection.

Analyze the following two testimony excerpts for contradictions:

TESTIMONY A (${witnessNameA}):
"${textA.substring(0, 500)}"
${contextA ? `Context: ${contextA.substring(0, 200)}` : ''}

TESTIMONY B (${witnessNameB}):
"${textB.substring(0, 500)}"
${contextB ? `Context: ${contextB.substring(0, 200)}` : ''}

Determine if these statements contradict each other. Consider:
1. Direct factual contradictions (dates, times, quantities, locations)
2. Logical inconsistencies (sequence of events, causal claims)
3. Implied contradictions (statements that cannot both be true given known facts)
4. Impossibility (claims that are physically or logically impossible)

Return a JSON object:
{
  "isContradiction": boolean,
  "type": "INTERNAL" | "EXTERNAL" | "EVIDENCE" | "IMPOSSIBILITY" | null,
  "severity": "HIGH" | "MEDIUM" | "LOW" | null,
  "reasoning": "detailed explanation of why these contradict or don't",
  "confidence": 0.0 to 1.0
}`;

  try {
    const response = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4o',
      messages: [
        { role: 'system', content: 'You are a precise legal contradiction detection AI. Return only valid JSON.' },
        { role: 'user', content: prompt },
      ],
      response_format: { type: 'json_object' },
      temperature: 0.1,
    });

    const result = JSON.parse(response.choices[0]?.message?.content || '{}');

    if (!result.isContradiction || !result.type) {
      return null;
    }

    return {
      type: result.type,
      severity: result.severity || 'MEDIUM',
      testimonyA: textA,
      testimonyB: textB,
      reasoning: result.reasoning || 'No reasoning provided',
      confidence: result.confidence || 0.5,
    };
  } catch (error) {
    console.error('[Veritas] OpenAI contradiction analysis error:', error);
    return null;
  }
}

/**
 * Generate cross-examination questions from a detected contradiction.
 */
export async function generateCrossExamQuestions(
  contradictions: ContradictionAnalysis[],
): Promise<CrossExaminationQuestion[]> {
  if (contradictions.length === 0) return [];

  const prompt = `You are a veteran trial attorney preparing for cross-examination.
Based on the following ${contradictions.length} detected contradictions in deposition testimony,
generate targeted cross-examination questions.

Contradictions:
${contradictions.map((c, i) => `
[${i + 1}] ${c.type} contradiction (${c.severity} severity, ${Math.round(c.confidence * 100)}% confidence):
  - Statement A: "${c.testimonyA.substring(0, 200)}"
  - Statement B: "${c.testimonyB.substring(0, 200)}"
  - Reasoning: ${c.reasoning}
`).join('\n')}

For each contradiction, generate one cross-examination question that:
1. References the specific statements
2. Creates a trap for the witness
3. Leads toward impeachment
4. Uses the evidence to lock in testimony

Return a JSON array of objects:
[{ "severity": "HIGH", "question": "...", "testimonyContext": "..." }]`;

  try {
    const response = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4o',
      messages: [
        { role: 'system', content: 'You are a ruthless cross-examiner. Return only valid JSON arrays.' },
        { role: 'user', content: prompt },
      ],
      response_format: { type: 'json_object' },
      temperature: 0.3,
    });

    const content = response.choices[0]?.message?.content || '[]';
    const parsed = JSON.parse(content);
    const questions = Array.isArray(parsed) ? parsed : (parsed.questions || []);
    return questions.slice(0, 15); // Limit to 15 questions
  } catch (error) {
    console.error('[Veritas] Cross-exam generation error:', error);
    return [];
  }
}

/**
 * Calculate a credibility score for a witness based on contradictions found.
 */
export function calculateCredibilityScore(
  totalContradictions: number,
  highSeverityCount: number,
  mediumSeverityCount: number,
): number {
  // Start at 85 (baseline for an expert witness)
  // Subtract 3 points per contradiction, 5 extra for HIGH severity, 2 extra for MEDIUM
  const score = Math.max(0, Math.min(100, 
    85 - (totalContradictions * 3) - (highSeverityCount * 5) - (mediumSeverityCount * 2)
  ));
  return Math.round(score);
}