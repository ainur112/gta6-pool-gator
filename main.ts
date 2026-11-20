// Entry program for gta6-clipper-01: copy VIDEO.json (the YouTube video's
// address) to /output, where the gate reads it. The entry is the video itself;
// the house reads its views from YouTube. Outside the grader, MAKEFUN_BOT_DIR
// and MAKEFUN_OUTPUT_DIR stand in for /bot and /output.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'VIDEO.json'), join(OUTPUT_DIR, 'VIDEO.json'));
} catch (err) {
  console.error(`VIDEO.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
