import { writeFile } from "node:fs/promises";
import path from "node:path";
import { generateSynthetic } from "../src/lib/synthetic/generate";

async function main() {
  const bundle = generateSynthetic();
  const dir = path.join(process.cwd(), "data", "synthetic");
  const json = (v: unknown) => `${JSON.stringify(v, null, 2)}\n`;
  await writeFile(path.join(dir, "athletes.json"), json(bundle.athletes));
  await writeFile(path.join(dir, "snapshots.json"), json(bundle.snapshots));
  await writeFile(path.join(dir, "meta.json"), json(bundle.meta));
  console.log(
    `seeded ${bundle.athletes.length} athletes, ${bundle.snapshots.length} snapshots, asOf=${bundle.meta.asOf}`,
  );
}

main();