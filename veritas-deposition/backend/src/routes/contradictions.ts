import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { detectContradictions, DetectionResult } from '../engine/contradiction-detector';

const router = Router();
const prisma = new PrismaClient();

// GET /api/veritas/contradictions — List contradictions
router.get('/', async (req: Request, res: Response) => {
  const { matterId, depositionId, severity, isResolved } = req.query;
  const where: any = {};
  if (matterId) where.matterId = matterId;
  if (depositionId) where.depositionId = depositionId;
  if (severity) where.severity = severity;
  if (isResolved !== undefined) where.isResolved = isResolved === 'true';
  const contradictions = await prisma.contradiction.findMany({
    where,
    include: { evidence: true, deposition: { select: { witnessName: true } } },
    orderBy: [{ severity: 'desc' }, { confidence: 'desc' }],
  });
  res.json(contradictions);
});

// GET /api/veritas/contradictions/:id — Get contradiction detail
router.get('/:id', async (req: Request, res: Response) => {
  const contradiction = await prisma.contradiction.findUnique({
    where: { id: req.params.id },
    include: { evidence: true, testimonyA: true, testimonyB: true },
  });
  if (!contradiction) return res.status(404).json({ error: 'Contradiction not found' });
  res.json(contradiction);
});

// PATCH /api/veritas/contradictions/:id/resolve — Mark as resolved
router.patch('/:id/resolve', async (req: Request, res: Response) => {
  const contradiction = await prisma.contradiction.update({
    where: { id: req.params.id },
    data: { isResolved: true, resolvedAt: new Date() },
  });
  res.json(contradiction);
});

// POST /api/veritas/contradictions/detect — Run full contradiction detection
router.post('/detect', async (req: Request, res: Response) => {
  const { depositionId } = req.body;
  if (!depositionId) {
    return res.status(400).json({ error: 'depositionId is required' });
  }

  try {
    // Run the contradiction detection pipeline
    const result: DetectionResult = await detectContradictions(depositionId);
    res.json({
      status: 'complete',
      depositionId: result.depositionId,
      contradictionsFound: result.contradictionsFound,
      credibilityScore: result.credibilityScore,
      crossExamQuestions: result.crossExamQuestions,
      processingTimeMs: result.processingTimeMs,
    });
  } catch (error: any) {
    console.error('[Veritas] Contradiction detection error:', error);
    res.status(500).json({
      status: 'error',
      error: error.message,
      depositionId,
    });
  }
});

export default router;