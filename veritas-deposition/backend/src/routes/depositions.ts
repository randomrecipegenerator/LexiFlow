import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

// GET /api/veritas/depositions — List depositions
router.get('/', async (req: Request, res: Response) => {
  const { matterId, witnessName, status } = req.query;
  const where: any = {};
  if (matterId) where.matterId = matterId;
  if (witnessName) where.witnessName = { contains: witnessName as string, mode: 'insensitive' };
  if (status) where.status = status;
  const depositions = await prisma.deposition.findMany({
    where,
    include: { _count: { select: { testimony: true, contradictions: true } } },
    orderBy: { date: 'desc' },
  });
  res.json(depositions);
});

// GET /api/veritas/depositions/:id — Get deposition detail
router.get('/:id', async (req: Request, res: Response) => {
  const deposition = await prisma.deposition.findUnique({
    where: { id: req.params.id },
    include: {
      matter: { select: { title: true, caseNumber: true } },
      testimony: { orderBy: { order: 'asc' } },
      contradictions: { include: { evidence: true }, orderBy: { severity: 'desc' } },
      documents: true,
    },
  });
  if (!deposition) return res.status(404).json({ error: 'Deposition not found' });
  res.json(deposition);
});

// POST /api/veritas/depositions — Create deposition
router.post('/', async (req: Request, res: Response) => {
  const { matterId, witnessName, witnessRole, date, durationMinutes, transcriptText, pageCount } = req.body;
  const deposition = await prisma.deposition.create({
    data: { matterId, witnessName, witnessRole, date: date ? new Date(date) : null, durationMinutes, transcriptText, pageCount },
  });
  res.status(201).json(deposition);
});

// POST /api/veritas/depositions/:id/upload — Upload transcript
router.post('/:id/upload', async (req: Request, res: Response) => {
  // In production, handle multipart upload with multer
  const { transcriptPath, transcriptText } = req.body;
  const deposition = await prisma.deposition.update({
    where: { id: req.params.id },
    data: { transcriptPath, transcriptText, status: 'UPLOADED' },
  });
  res.json({ status: 'uploaded', deposition });
});

// POST /api/veritas/depositions/:id/process — Trigger AI processing
router.post('/:id/process', async (req: Request, res: Response) => {
  const deposition = await prisma.deposition.update({
    where: { id: req.params.id },
    data: { status: 'PROCESSING' },
  });
  // In production, this enqueues a background job for AI analysis
  res.json({ status: 'processing_started', depositionId: deposition.id });
});

export default router;