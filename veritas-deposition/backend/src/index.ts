import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { PrismaClient } from '@prisma/client';
import matterRoutes from './routes/matters';
import depositionRoutes from './routes/depositions';
import evidenceRoutes from './routes/evidence';
import contradictionRoutes from './routes/contradictions';
import analysisRoutes from './routes/analysis';

const prisma = new PrismaClient();
const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Health check
app.get('/api/veritas/health', async (req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    res.json({ status: 'healthy', database: 'connected', service: 'Veritas Deposition™', version: '1.0.0' });
  } catch (e) {
    res.status(503).json({ status: 'unhealthy', database: 'disconnected', error: (e as Error).message });
  }
});

// Routes
app.use('/api/veritas/matters', matterRoutes);
app.use('/api/veritas/depositions', depositionRoutes);
app.use('/api/veritas/evidence', evidenceRoutes);
app.use('/api/veritas/contradictions', contradictionRoutes);
app.use('/api/veritas/analysis', analysisRoutes);

// Error handler
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('[Veritas Error]', err.message);
  res.status(500).json({ error: 'Internal server error', message: err.message });
});

// Start server
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`⚖️  Veritas Deposition™ API running on port ${PORT}`);
    console.log(`📡 Health: http://localhost:${PORT}/api/veritas/health`);
  });
}

export { app, prisma };