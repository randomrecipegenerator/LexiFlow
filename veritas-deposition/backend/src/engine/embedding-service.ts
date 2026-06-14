import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

/**
 * Generate an embedding vector for a text segment using OpenAI's text-embedding-ada-002.
 * Used for semantic similarity search in contradiction detection (pgvector).
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  try {
    const response = await openai.embeddings.create({
      model: 'text-embedding-ada-002',
      input: text.substring(0, 8000), // Ada-002 has an 8k token limit
    });
    return response.data[0].embedding;
  } catch (error) {
    console.error('[Veritas] Embedding generation error:', error);
    // Return a zero vector as fallback (will not match any semantic search)
    return new Array(1536).fill(0);
  }
}

/**
 * Generate embeddings for an array of testimony segments.
 */
export async function generateEmbeddingsBatch(
  segments: { id: string; text: string }[],
): Promise<Array<{ id: string; embedding: number[] }>> {
  const results: Array<{ id: string; embedding: number[] }> = [];
  
  // Process in batches of 20 to avoid rate limits
  const batchSize = 20;
  for (let i = 0; i < segments.length; i += batchSize) {
    const batch = segments.slice(i, i + batchSize);
    const embeddings = await Promise.all(
      batch.map(s => generateEmbedding(s.text).then(emb => ({ id: s.id, embedding: emb })))
    );
    results.push(...embeddings);
  }
  
  return results;
}

/**
 * Parse a deposition transcript into structured testimony segments.
 * Each segment is a Q&A pair or a block of continuous testimony.
 */
export function parseTranscriptIntoSegments(
  transcriptText: string,
  depositionId: string,
): Array<{
  text: string;
  speaker: string;
  pageNumber?: number;
  lineNumber?: number;
  timestamp?: string;
}> {
  // Split by page markers (common in legal transcripts)
  const lines = transcriptText.split('\n');
  const segments: Array<{
    text: string;
    speaker: string;
    pageNumber?: number;
    lineNumber?: number;
    timestamp?: string;
  }> = [];
  
  let currentPage = 1;
  let currentLine = 1;
  let currentSpeaker = 'WITNESS';
  let currentBuffer = '';

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Detect page markers: "Page 42" or "[Page 42]" or "42"
    const pageMatch = trimmed.match(/^\[?Page\s+(\d+)\]?$/i);
    if (pageMatch) {
      currentPage = parseInt(pageMatch[1]);
      currentLine = 1;
      continue;
    }

    // Detect speaker changes: "Q." or "A." or "MR. SMITH:" or "BY MR. JONES:"
    const speakerMatch = trimmed.match(/^(Q\.|A\.|BY\s+[\w\s]+:)\s*/i);
    if (speakerMatch) {
      // Flush previous buffer
      if (currentBuffer.length > 20) {
        segments.push({
          text: currentBuffer.trim(),
          speaker: currentSpeaker,
          pageNumber: currentPage,
          lineNumber: Math.max(1, currentLine - 1),
        });
      }
      
      currentSpeaker = speakerMatch[1].startsWith('Q') ? 'COUNSEL' : 'WITNESS';
      currentBuffer = trimmed.replace(speakerMatch[0], '').trim();
    } else {
      // Continuation of current speaker's testimony
      if (currentBuffer) currentBuffer += ' ' + trimmed;
      else currentBuffer = trimmed;
    }
    currentLine++;
  }

  // Flush final buffer
  if (currentBuffer.length > 20) {
    segments.push({
      text: currentBuffer.trim(),
      speaker: currentSpeaker,
      pageNumber: currentPage,
    });
  }

  return segments;
}

/**
 * Compute cosine similarity between two embedding vectors.
 */
export function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) return 0;
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  if (normA === 0 || normB === 0) return 0;
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Find semantically similar testimony segments using cosine similarity.
 * Used when pgvector query is not available (fallback).
 */
export function findSimilarSegments(
  queryEmbedding: number[],
  segments: Array<{ id: string; text: string; embedding?: number[] }>,
  topK: number = 10,
  threshold: number = 0.75,
): Array<{ id: string; text: string; similarity: number }> {
  const scored = segments
    .filter(s => s.embedding && s.embedding.length > 0)
    .map(s => ({
      id: s.id,
      text: s.text,
      similarity: cosineSimilarity(queryEmbedding, s.embedding!),
    }))
    .filter(s => s.similarity >= threshold)
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, topK);

  return scored;
}