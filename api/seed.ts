import { generateSynthetic } from "../src/lib/synthetic/generate";
import { prisma } from "./db";

async function main() {
  if ((await prisma.athlete.count()) > 0) {
    console.log("seed skipped: roster already present");
    return;
  }
  const bundle = generateSynthetic();

  await prisma.athlete.createMany({
    data: bundle.athletes.map((a) => ({
      id: a.id,
      lastName: a.lastName,
      firstName: a.firstName,
      position: a.position,
      previousInjury: a.previousInjury,
    })),
  });

  const chunk = 400;
  for (let i = 0; i < bundle.snapshots.length; i += chunk) {
    await prisma.dailySnapshot.createMany({
      data: bundle.snapshots.slice(i, i + chunk),
    });
  }

  await prisma.meta.create({
    data: {
      id: 1,
      asOf: bundle.meta.asOf,
      seedKey: bundle.meta.seedKey,
    },
  });

  console.log(
    `seeded ${bundle.athletes.length} athletes, ${bundle.snapshots.length} snapshots`,
  );
}

main()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });