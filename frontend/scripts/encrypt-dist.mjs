
import dotenv from "dotenv";
import { spawnSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";

const projectRoot = resolve(
  dirname(fileURLToPath(import.meta.url)),
  ".."
);

// Lokale .env liegt eine Ebene über frontend.
// In GitHub Actions wird die Umgebungsvariable direkt übergeben.
const envPath = resolve(projectRoot, "../.env");
dotenv.config({ path: envPath });

if (!process.env.STATICRYPT_PASSWORD) {
  throw new Error("STATICRYPT_PASSWORD fehlt!");
}

const distDir = resolve(projectRoot, "dist");
const indexFile = resolve(distDir, "index.html");
const staticryptCli = resolve(
  projectRoot,
  "node_modules",
  "staticrypt",
  "cli",
  "index.js"
);

if (!existsSync(indexFile)) {
  throw new Error("dist/index.html wurde nicht gefunden!");
}

if (!existsSync(staticryptCli)) {
  throw new Error("StatiCrypt CLI wurde nicht gefunden!");
}

console.log("Starte Verschlüsselung...");

const result = spawnSync(
  process.execPath,
  [
    staticryptCli,
    "index.html",
    "-d",
    ".",
    "--remember",
    "false",
    "--template-title",
    "Geschützter Bereich",
    "--template-placeholder",
    "Passwort eingeben",
    "--template-button",
    "Login",
    "--template-error",
    "Falsches Passwort. Bitte erneut versuchen."
  ],
  {
    cwd: distDir,
    env: process.env,
    stdio: "inherit"
  }
);

if (result.error) {
  throw result.error;
}

if (result.status !== 0) {
  throw new Error("Die Verschlüsselung ist fehlgeschlagen!");
}

console.log("Website erfolgreich verschlüsselt!");
