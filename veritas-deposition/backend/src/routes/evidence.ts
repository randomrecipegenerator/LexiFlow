import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

// GET /api/veritas/evidence — List evidence
router.get('/', async (req: Request, res: Response) => {
  const { matterId, evidenceType } = req.query;
  const where: any = {};
  if (matterId) where.matterId = matterId;
  if (evidenceType) where.evidenceType = evidenceType;
  const evidence = await prisma.evidence.findMany({
    where,
    include: { contradictions: { select: { id: true, severity: true, reasoning: true } } },
    orderBy: { createdAt: 'desc' },
  });
  res.json(evidence);
});

// POST /api/veritas/evidence — Create evidence
router.post('/', async (req: Request, res: Response) => {
  const { matterId, depositionId, title, evidenceType, description } = req.body;
  const evidence = await prisma.evidence.create({
    data: { matterId, depositionId, title, evidenceType, description },
  });
  res.status(201).json(evidence);
});

// POST /api/veritas/evidence/:id/upload — Upload evidence file
router.post('/:id/upload', async (req: Request, res: Response) => {
  const { filePath, fileHash, exhibitNumber } = req.body;
  const evidence = await prisma.evidence.update({
    where: { id: req.params.id },
    data: { filePath, fileHash, exhibitNumber },
  });
  res.json({ status: 'uploaded', evidence });
});

export default router;