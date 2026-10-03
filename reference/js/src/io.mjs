import fs from 'node:fs';

export function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

export function unwrapVector(doc) {
  if (doc && typeof doc === 'object' && doc.input && typeof doc.input === 'object') return doc.input;
  return doc;
}

export function printJson(value) {
  process.stdout.write(JSON.stringify(value, null, 2) + '\n');
}
