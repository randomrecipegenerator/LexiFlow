import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

// GET /api/veritas/matters — List all matters
router.get('/', async (req: Request, res: Response) => {
  const { status, firmId, search, page = '1', limit = '20' } = req.query;
  const skip = (parseInt(page as string) - 1) * parseInt(limit as string);
  const where: any = {};
  if (status) where.status = status;
  if (firmId) where.firmId = firmId;
  if (search) where.OR = [
    { title: { contains: search as string, mode: 'insensitive' } },
    { caseNumber: { contains: search as string, mode: 'insensitive' } },
  ];
  const [matters, total] = await Promise.all([
    prisma.matter.findMany({
      where, skip, take: parseInt(limit as string),
      include: { _count: { select: { depositions: true, evidence: true, contradictions: true } } },
      orderBy: { updatedAt: 'desc' },
    }),
    prisma.matter.count({ where }),
  ]);
  res.json({ matters, total, page: parseInt(page as string), limit: parseInt(limit as string) });
});

// GET /api/veritas/matters/:id — Get matter detail
router.get('/:id', async (req: Request, res: Response) => {
  const matter = await prisma.matter.findUnique({
    where: { id: req.params.id },
    include: {
      depositions: { orderBy: { date: 'desc' } },
      evidence: true,
      witnesses: true,
      contradictions: { where: { isResolved: false }, orderBy: { severity: 'desc' } },
      documents: { orderBy: { createdAt: 'desc' } },
    },
  });
  if (!matter) return res.status(404).json({ error: 'Matter not found' });
  res.json(matter);
});

// POST /api/veritas/matters — Create matter
router.post('/', async (req: Request, res: Response) => {
  const { title, caseNumber, caseType, jurisdiction, court, plaintiffName, defendantName, firmId } = req.body;
  const matter = await prisma.matter.create({
    data: { title, caseNumber, caseType, jurisdiction, court, plaintiffName, defendantName, firmId },
  });
  res.status(201).json(matter);
});

// PUT /api/veritas/matters/:id — Update matter
router.put('/:id', async (req: Request, res: Response) => {
  const matter = await prisma.matter.update({
    where: { id: req.params.id },
    data: req.body,
  });
  res.json(matter);
});

// DELETE /api/veritas/matters/:id — Delete matter
router.delete('/:id', async (req: Request, res: Response) => {
  await prisma.matter.delete({ where: { id: req.params.id } });
  res.status(204).send();
});

// POST /api/veritas/matters/:id/sync — Sync matter from CRM
router.post('/:id/sync', async (req: Request, res: Response) => {
  const { externalId, crmType } = req.body; // crmType: "filevine" | "clio"
  const matter = await prisma.matter.update({
    where: { id: req.params.id },
    data: { externalId },
  });
  res.json({ status: 'synced', matter, crmType });
});

export default router;