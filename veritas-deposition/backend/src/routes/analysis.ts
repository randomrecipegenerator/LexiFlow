import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

// GET /api/veritas/analysis/summary/:depositionId — Get AI analysis summary
router.get('/summary/:depositionId', async (req: Request, res: Response) => {
  const analysis = await prisma.aiAnalysis.findUnique({
    where: { depositionId: req.params.depositionId },
  });
  if (!analysis) return res.status(404).json({ error: 'Analysis not found. Run /process first.' });
  res.json(analysis);
});

// POST /api/veritas/analysis/contradictions — Bulk contradiction detection
router.post('/contradictions', async (req: Request, res: Response) => {
  const { matterId } = req.body;
  // In production: orchestrate RAG pipeline
  // 1. Embed all testimony segments
  // 2. Cross-reference with evidence embeddings
  // 3. Identify semantic contradictions
  // 4. Return structured contradictions
  res.json({ status: 'pipeline_triggered', matterId, note: 'Async processing started' });
});

// POST /api/veritas/analysis/cross-examine — Generate cross-exam questions
router.post('/cross-examine', async (req: Request, res: Response) => {
  const { depositionId } = req.body;
  const contradictions = await prisma.contradiction.findMany({
    where: { depositionId, isResolved: false },
    orderBy: { severity: 'desc' },
  });
  // Generate cross-exam questions from contradictions
  const questions = contradictions.map(c => ({
    contradictionId: c.id,
    severity: c.severity,
    question: `Regarding your testimony that "${c.testimonyTextA.substring(0, 80)}..." — can you reconcile this with ${c.testimonyTextB ? `your earlier statement that "${c.testimonyTextB.substring(0, 80)}..."` : 'the documentary evidence'}?`,
  }));
  res.json({ depositionId, questionsCount: questions.length, questions });
});

// POST /api/veritas/analysis/credibility — Update witness credibility score
router.post('/credibility', async (req: Request, res: Response) => {
  const { depositionId } = req.body;
  const contradictions = await prisma.contradiction.findMany({ where: { depositionId } });
  const totalContradictions = contradictions.length;
  const highCount = contradictions.filter(c => c.severity === 'HIGH').length;
  const score = Math.max(0, Math.min(100, 85 - (totalContradictions * 3) - (highCount * 5)));
  await prisma.deposition.update({ where: { id: depositionId }, data: { credibilityScore: score } });
  await prisma.aiAnalysis.upsert({
    where: { depositionId },
    update: { credibilityScore: score, contradictions: totalContradictions },
    create: { depositionId, credibilityScore: score, contradictions: totalContradictions, keyAdmissions: 0 },
  });
  res.json({ depositionId, credibilityScore: score, totalContradictions });
});

export default router;