/**
 * LexiFlow Desktop — Local PII/PHI Redaction Utility
 * 
 * Scans documents for PII/PHI patterns (SSN, DOB, patient IDs, etc.)
 * and creates redacted copies by masking detected patterns.
 * 
 * Supports: Plain text (.txt, .csv) and basic PDF redaction.
 * For advanced PDF/image redaction, delegates to the cloud API.
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class RedactUtils {
    constructor(options = {}) {
        this.options = {
            redactionChar: options.redactionChar || '█',  // Full block
            backupOriginal: options.backupOriginal !== false,
            outputDir: options.outputDir || null, // null = same dir as input
            ...options,
        };

        // PII/PHI Patterns to detect
        this.patterns = [
            // Social Security Numbers
            { name: 'SSN', pattern: /\b\d{3}-\d{2}-\d{4}\b/g, severity: 'critical' },
            { name: 'SSN (condensed)', pattern: /\b\d{9}\b/g, severity: 'critical' },
            
            // Phone Numbers
            { name: 'Phone', pattern: /\b\d{3}[-.)]\s?\d{3}[-.]\d{4}\b/g, severity: 'medium' },
            
            // Dates of Birth
            { name: 'DOB', pattern: /\b(?:DOB|Date of Birth|Born|Birthdate)[:\s]*[\d\/\-]+\b/gi, severity: 'high' },
            { name: 'DOB (MM/DD/YYYY)', pattern: /\b\d{1,2}\/\d{1,2}\/\d{4}\b/g, severity: 'high' },
            
            // Email Addresses
            { name: 'Email', pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, severity: 'medium' },
            
            // Medical Record Numbers
            { name: 'MRN', pattern: /\b(?:MRN|Medical Record|Chart|Patient ID)[:\s#]*[A-Z0-9\-]{4,16}\b/gi, severity: 'high' },
            
            // Health Insurance / Policy IDs
            { name: 'Health Insurance ID', pattern: /\b(?:HIC|Health Insurance|Policy|Member ID|Subscriber)[:\s#]*[A-Z0-9\-]{4,20}\b/gi, severity: 'high' },
            
            // Medicare/Medicaid IDs
            { name: 'Medicare ID', pattern: /\b\d{11}\b/g, severity: 'high' },
            
            // Credit Card Numbers (PCI)
            { name: 'Credit Card', pattern: /\b(?:\d{4}[-\s]?){3}\d{4}\b/g, severity: 'critical' },
            
            // Driver's License (various state formats)
            { name: 'Driver License', pattern: /\b(?:DL|Driver.?License|License.?No)[:\s#]*[A-Z0-9\-]{4,20}\b/gi, severity: 'high' },
            
            // IP Addresses
            { name: 'IP Address', pattern: /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, severity: 'low' },
            
            // Account Numbers
            { name: 'Account Number', pattern: /\b(?:Acct|Account|Accnt)[:\s#]*\d{4,12}\b/gi, severity: 'high' },

            // Patient Address
            { name: 'Street Address', pattern: /\b\d{1,5}\s[A-Za-z0-9\s.,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Circle|Cir)\b/gi, severity: 'medium' },
        ];
    }

    // =========================================================================
    // Scan a file for PII patterns (no modification, just detection)
    // =========================================================================

    async scanFile(filePath) {
        if (!fs.existsSync(filePath)) {
            throw new Error(`File not found: ${filePath}`);
        }

        const ext = path.extname(filePath).toLowerCase();
        let content = '';

        if (ext === '.txt' || ext === '.csv' || ext === '.md') {
            content = fs.readFileSync(filePath, 'utf-8');
        } else if (ext === '.pdf') {
            // Basic PDF text extraction via simple buffer read
            // For full PDF support, use pdf-parse or similar library
            content = fs.readFileSync(filePath, 'utf-8');
        } else {
            return {
                file: filePath,
                supported: false,
                message: `File type ${ext} not supported for text scanning. Use image-based redaction for this format.`,
                findings: [],
            };
        }

        const findings = [];
        const seen = new Set();

        for (const p of this.patterns) {
            const matches = content.matchAll(p.pattern);
            for (const match of matches) {
                const key = `${p.name}:${match[0]}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    findings.push({
                        type: p.name,
                        severity: p.severity,
                        value: match[0],
                        index: match.index,
                    });
                }
            }
        }

        // Deduplicate by grouping
        const grouped = {};
        for (const f of findings) {
            if (!grouped[f.type]) grouped[f.type] = [];
            grouped[f.type].push(f.value);
        }

        return {
            file: filePath,
            supported: true,
            totalFindings: findings.length,
            findings,
            summary: Object.entries(grouped).map(([type, values]) => ({
                type,
                count: values.length,
                severity: this.patterns.find(p => p.name === type)?.severity || 'unknown',
                examples: [...new Set(values)].slice(0, 3),
            })),
        };
    }

    // =========================================================================
    // Redact a file (create a redacted copy)
    // =========================================================================

    async redactFile(filePath) {
        if (!fs.existsSync(filePath)) {
            throw new Error(`File not found: ${filePath}`);
        }

        // First, scan for PII
        const scanResult = await this.scanFile(filePath);

        if (!scanResult.supported) {
            return {
                file: filePath,
                outputPath: filePath,
                redactedCount: 0,
                supported: false,
                message: scanResult.message,
                log: {},
            };
        }

        if (scanResult.totalFindings === 0) {
            return {
                file: filePath,
                outputPath: filePath,
                redactedCount: 0,
                supported: true,
                message: 'No PII/PHI found in this file.',
                log: {},
            };
        }

        // Read the file content
        let content = fs.readFileSync(filePath, 'utf-8');
        const ext = path.extname(filePath);
        const baseName = path.basename(filePath, ext);
        const dir = this.options.outputDir || path.dirname(filePath);

        // Create output directory if needed
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        // Backup original
        if (this.options.backupOriginal) {
            const backupPath = path.join(dir, `${baseName}.original${ext}`);
            fs.copyFileSync(filePath, backupPath);
        }

        // Apply redaction — mask each finding
        let redactedCount = 0;
        const redactionLog = {};

        for (const p of this.patterns) {
            let match;
            // Reset lastIndex
            p.pattern.lastIndex = 0;
            
            while ((match = p.pattern.exec(content)) !== null) {
                const masked = this.options.redactionChar.repeat(match[0].length);
                content = content.substring(0, match.index) + masked + content.substring(match.index + match[0].length);
                redactedCount++;
                
                if (!redactionLog[p.name]) redactionLog[p.name] = 0;
                redactionLog[p.name]++;

                // Reset lastIndex since we modified the string
                p.pattern.lastIndex = match.index + masked.length;
            }
        }

        // Write the redacted file
        const outputPath = path.join(dir, `${baseName}_redacted${ext}`);
        fs.writeFileSync(outputPath, content, 'utf-8');

        return {
            file: filePath,
            outputPath,
            redactedCount,
            supported: true,
            message: `Redacted ${redactedCount} PII/PHI fields. Redacted copy saved to: ${outputPath}`,
            log: redactionLog,
            summary: Object.entries(redactionLog).map(([type, count]) => ({
                type,
                count,
            })),
        };
    }

    // =========================================================================
    // Batch redact all files in a folder
    // =========================================================================

    async batchRedactFolder(folderPath, fileExtensions = ['.txt', '.csv', '.md']) {
        if (!fs.existsSync(folderPath)) {
            throw new Error(`Folder not found: ${folderPath}`);
        }

        const files = this._scanFolder(folderPath);
        const results = [];

        for (const filePath of files) {
            const ext = path.extname(filePath).toLowerCase();
            if (fileExtensions.includes(ext)) {
                try {
                    const result = await this.redactFile(filePath);
                    results.push(result);
                } catch (err) {
                    results.push({
                        file: filePath,
                        error: err.message,
                        redactedCount: 0,
                    });
                }
            }
        }

        const total = results.reduce((sum, r) => sum + (r.redactedCount || 0), 0);
        return {
            totalFiles: files.length,
            processedFiles: results.length,
            totalRedactions: total,
            results,
        };
    }

    // =========================================================================
    // Helpers
    // =========================================================================

    _scanFolder(dirPath) {
        const files = [];
        try {
            const entries = fs.readdirSync(dirPath, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                if (entry.isDirectory() && !entry.name.startsWith('.')) {
                    files.push(...this._scanFolder(fullPath));
                } else if (entry.isFile()) {
                    files.push(fullPath);
                }
            }
        } catch (err) {
            console.error(`[RedactUtils] Scan error: ${err.message}`);
        }
        return files;
    }
}

module.exports = { RedactUtils };