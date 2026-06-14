export interface Matter {
  id: string;
  name: string;
  caseNumber: string;
  court: string;
  witnessCount: number;
  transcriptCount: number;
  status: 'active' | 'trial' | 'discovery' | 'closed';
  dateUpdated: string;
}

export interface Witness {
  id: string;
  name: string;
  role: 'plaintiff' | 'defendant' | 'expert' | 'fact' | 'medical';
  riskScore: number;
  transcriptCount: number;
  contradictions: number;
  credibility: number;
  avatar?: string;
}

export interface Contradiction {
  id: string;
  witnessId: string;
  type: 'internal' | 'external' | 'medical' | 'timeline';
  severity: 'high' | 'medium' | 'low';
  description: string;
  sourceTranscript: string;
  sourceLine: number;
  supportingDoc?: string;
}

export interface Transcript {
  id: string;
  witnessId: string;
  title: string;
  date: string;
  pages: number;
  deponent: string;
  keyFindings: string[];
}

export interface EvidenceItem {
  id: string;
  name: string;
  type: 'medical' | 'photo' | 'document' | 'video' | 'audio';
  date: string;
  witnessIds: string[];
  fileUrl: string;
}

export type UploadCategory = 'transcript' | 'medical' | 'evidence' | 'photograph' | 'video';