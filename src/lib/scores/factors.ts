export type InjuryFactors = {
  workloadSpike: number;
  sleepDebt: number;
  hrvDrop: number;
  previousInjury: number;
};

export function breakdownFactors(input: {
  spike: number;
  sleepDebt: number;
  hrvDrop: number;
  hist: number;
}): InjuryFactors {
  const previousInjuryRaw = input.hist > 0 ? Math.max(0, input.hist) : 0;
  const weights = {
    workloadSpike: Math.max(0, input.spike),
    sleepDebt: Math.max(0, input.sleepDebt),
    hrvDrop: Math.max(0, input.hrvDrop),
    previousInjury: previousInjuryRaw,
  };
  const keys = Object.keys(weights) as (keyof InjuryFactors)[];
  const sum = keys.reduce((a, k) => a + weights[k], 0);

  if (sum === 0) {
    if (input.hist <= 0) {
      return {
        workloadSpike: 34,
        sleepDebt: 33,
        hrvDrop: 33,
        previousInjury: 0,
      };
    }
    return {
      workloadSpike: 25,
      sleepDebt: 25,
      hrvDrop: 25,
      previousInjury: 25,
    };
  }

  const raw = keys.map((k) => ({
    k,
    v: (weights[k] / sum) * 100,
  }));
  const rounded = raw.map((r) => ({ k: r.k, v: Math.round(r.v) }));
  if (input.hist <= 0) {
    const inj = rounded.find((r) => r.k === "previousInjury");
    if (inj) inj.v = 0;
  }
  let total = rounded.reduce((a, r) => a + r.v, 0);
  const delta = 100 - total;
  if (delta !== 0) {
    const target =
      rounded
        .filter((r) => input.hist > 0 || r.k !== "previousInjury")
        .sort((a, b) => b.v - a.v)[0] ?? rounded[0];
    target.v += delta;
  }
  return Object.fromEntries(rounded.map((r) => [r.k, r.v])) as InjuryFactors;
}