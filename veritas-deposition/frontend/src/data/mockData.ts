export const mockMatters = [
  { id: 'm1', name: 'Smith v. Pacific Medical', caseNumber: '2024-CV-00421', court: 'CA Superior Court', witnessCount: 8, transcriptCount: 14, status: 'trial' as const, dateUpdated: '2026-06-10' },
  { id: 'm2', name: 'Johnson v. St. Mary\'s Hospital', caseNumber: '2025-CV-00189', court: 'NY Supreme Court', witnessCount: 12, transcriptCount: 22, status: 'active' as const, dateUpdated: '2026-06-08' },
  { id: 'm3', name: 'Rodriguez v. County General', caseNumber: '2025-CV-00342', court: 'TX District Court', witnessCount: 6, transcriptCount: 9, status: 'discovery' as const, dateUpdated: '2026-06-05' },
  { id: 'm4', name: 'Chen v. Northwest Health', caseNumber: '2024-CV-00567', court: 'WA Superior Court', witnessCount: 10, transcriptCount: 18, status: 'active' as const, dateUpdated: '2026-06-03' },
  { id: 'm5', name: 'Williams v. Eagle Ridge', caseNumber: '2025-CV-00112', court: 'IL Circuit Court', witnessCount: 5, transcriptCount: 7, status: 'closed' as const, dateUpdated: '2026-05-28' },
]

export const mockWitnesses = [
  { id: 'w1', name: 'Dr. Sarah Chen', role: 'expert' as const, riskScore: 72, transcriptCount: 4, contradictions: 2, credibility: 85 },
  { id: 'w2', name: 'James Morrison', role: 'plaintiff' as const, riskScore: 45, transcriptCount: 3, contradictions: 0, credibility: 92 },
  { id: 'w3', name: 'Nurse Rebecca Torres', role: 'fact' as const, riskScore: 28, transcriptCount: 2, contradictions: 0, credibility: 95 },
  { id: 'w4', name: 'Dr. Michael Park', role: 'defendant' as const, riskScore: 88, transcriptCount: 5, contradictions: 4, credibility: 62 },
  { id: 'w5', name: 'Dr. Lisa Park', role: 'medical' as const, riskScore: 55, transcriptCount: 3, contradictions: 1, credibility: 78 },
]

export const mockContradictions = [
  { id: 'c1', witnessId: 'w1', type: 'medical' as const, severity: 'high' as const, description: 'Estimated time of intubation differs by 12 minutes from nursing notes', sourceTranscript: 'Chen Dep. Day 2, p.45', sourceLine: 1123, supportingDoc: 'Nursing Flow Sheet - Page 4' },
  { id: 'c2', witnessId: 'w4', type: 'internal' as const, severity: 'high' as const, description: 'Contradicts own preliminary report on timing of medication administration', sourceTranscript: 'Park Dep. Day 1, p.89', sourceLine: 2214, supportingDoc: 'Preliminary Assessment Report' },
  { id: 'c3', witnessId: 'w1', type: 'timeline' as const, severity: 'medium' as const, description: 'Timeline of patient stabilization conflicts with ER intake records', sourceTranscript: 'Chen Dep. Day 2, p.102', sourceLine: 2543 },
  { id: 'c4', witnessId: 'w4', type: 'external' as const, severity: 'high' as const, description: 'Expert witness testimony contradicts published standard of care guidelines', sourceTranscript: 'Park Dep. Day 2, p.34', sourceLine: 834, supportingDoc: 'ACOG Practice Bulletin No. 183' },
  { id: 'c5', witnessId: 'w5', type: 'medical' as const, severity: 'low' as const, description: 'Minor discrepancy in reported patient weight', sourceTranscript: 'Park Dep. Day 1, p.156', sourceLine: 3887 },
]