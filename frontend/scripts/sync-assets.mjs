import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(here, "..");
const repoRoot = resolve(frontendRoot, "..");
const processedRoot = resolve(repoRoot, "assets", "processed");
const manifestPath = resolve(repoRoot, "assets", "assets-manifest.json");
const outputRoot = resolve(frontendRoot, "public", "media");

const directories = [
  "brand",
  "kitchens_real",
  "facades",
  "colors",
  "handles",
  "countertops",
];

if (!existsSync(processedRoot)) {
  throw new Error(`Processed assets directory is missing: ${processedRoot}`);
}

rmSync(outputRoot, { recursive: true, force: true });
mkdirSync(outputRoot, { recursive: true });

for (const directory of directories) {
  const source = resolve(processedRoot, directory);
  if (existsSync(source)) {
    cpSync(source, resolve(outputRoot, directory), { recursive: true });
  }
}

if (existsSync(manifestPath)) {
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  writeFileSync(resolve(outputRoot, "assets-manifest.json"), JSON.stringify(manifest, null, 2));
}

console.log(`Synced frontend media to ${outputRoot}`);
