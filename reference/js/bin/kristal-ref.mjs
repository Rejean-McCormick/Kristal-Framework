#!/usr/bin/env node
import { main } from '../src/cli.mjs';
main().catch((error) => {
  process.stderr.write((error?.stack ?? String(error)) + '\n');
  process.exit(2);
});
