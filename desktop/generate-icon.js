#!/usr/bin/env node
/**
 * Generate a simple LexiFlow app icon (PNG).
 * Creates a 256x256 icon with navy background and gold "LF" text.
 * Uses pure Node.js Buffer operations to craft a valid PNG.
 */
const fs = require('fs');
const path = require('path');

// Minimal 16x16 PNG with navy/gold brand colors
// We'll generate a proper PNG using raw bytes
function createMinimalPNG(size) {
  // Create a simple valid PNG
  // PNG signature
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  // IHDR chunk
  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(size, 0);  // width
  ihdrData.writeUInt32BE(size, 4);  // height
  ihdrData.writeUInt8(8, 8);        // bit depth
  ihdrData.writeUInt8(2, 9);        // color type (RGB)
  ihdrData.writeUInt8(0, 10);       // compression
  ihdrData.writeUInt8(0, 11);       // filter
  ihdrData.writeUInt8(0, 12);       // interlace

  const ihdr = createChunk('IHDR', ihdrData);

  // IDAT chunk - raw image data (navy blue fill with gold LF shape)
  // For simplicity, generate a navy rectangle with gold pixels in the center
  const rawData = [];
  const navy = [26, 58, 92];    // #1a3a5c
  const gold = [201, 168, 76];  // #c9a84c

  for (let y = 0; y < size; y++) {
    rawData.push(0); // filter byte (none)
    for (let x = 0; x < size; x++) {
      // Gold "LF" pattern in the center
      const cx = Math.floor(size / 2);
      const cy = Math.floor(size / 2);
      const rx = Math.floor(size * 0.35);
      const ry = Math.floor(size * 0.35);
      const isGold = false;
      // Simple centered square pattern
      if (x > cx - rx && x < cx + rx && y > cy - ry && y < cy + ry) {
        // L shape
        const lx = x - (cx - rx);
        const ly = y - (cy - ry);
        const lw = rx * 2;
        const lh = ry * 2;
        const barW = Math.floor(lw * 0.25);
        const barH = Math.floor(lh * 0.65);

        if (lx < barW && ly < lh) {
          // Vertical bar of L
          rawData.push(...gold);
        } else if (ly > lh - barW && lx < lw) {
          // Horizontal bar of L
          rawData.push(...gold);
        } else {
          rawData.push(...navy);
        }
      } else {
        rawData.push(...navy);
      }
    }
  }

  // Compress with zlib (using a helper since we can't import zlib in this script directly)
  const zlib = require('zlib');
  const compressed = zlib.deflateSync(Buffer.from(rawData));
  const idat = createChunk('IDAT', compressed);

  // IEND chunk
  const iend = createChunk('IEND', Buffer.alloc(0));

  return Buffer.concat([signature, ihdr, idat, iend]);
}

function createChunk(type, data) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const typeBuffer = Buffer.from(type, 'ascii');
  const crcData = Buffer.concat([typeBuffer, data]);
  const crc = crc32(crcData);
  const crcBuffer = Buffer.alloc(4);
  crcBuffer.writeUInt32BE(crc, 0);
  return Buffer.concat([length, typeBuffer, data, crcBuffer]);
}

function crc32(buf) {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) {
    crc ^= buf[i];
    for (let j = 0; j < 8; j++) {
      if (crc & 1) {
        crc = (crc >>> 1) ^ 0xEDB88320;
      } else {
        crc = crc >>> 1;
      }
    }
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

// Generate 256x256 icon
const png = createMinimalPNG(256);
const outputPath = path.join(__dirname, 'app-icon.png');
fs.writeFileSync(outputPath, png);
console.log(`Icon generated: ${outputPath} (${png.length} bytes)`);