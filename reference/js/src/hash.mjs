import crypto from 'node:crypto';

export function sha256Hex(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

export function sha256Id(bytes) {
  return `sha256:${sha256Hex(bytes)}`;
}
