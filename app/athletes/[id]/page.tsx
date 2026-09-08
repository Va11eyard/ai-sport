import { Suspense } from "react";
import { AthleteDetailView } from "@/components/AthleteDetailView";
import { SourceUnavailable, isSourceError } from "@/components/SourceUnavailable";
import { getDay } from "@/lib/entry/client";
import { addDays } from "@/lib/scores/math";
import { getAdapter } from "@/lib/wearables/getAdapter";
import { notFound } from "next/navigation";
import Loading from "../../loading";

export default function AthletePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return (
    <Suspense fallback={<Loading />}>
      <AthletePageBody params={params} />
    </Suspense>
  );
}

async function AthletePageBody({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const adapter = getAdapter();
    const asOf = await adapter.asOf();
    const roster = await adapter.roster();
    const athlete = roster.find((a) => a.id === id);
    if (!athlete) notFound();
    const from = addDays(asOf, -89);
    const series90 = await adapter.athleteSeries(id, from, asOf);
    const recs = await adapter.todayRecommendations(id, asOf);
    const factors = await adapter.injuryFactorBreakdown(id, asOf);
    const day = await getDay(id, asOf).catch(() => null);
    const analysis = await adapter.todayAnalysis(id, asOf).catch(() => ({
      status: "upstream_error" as const,
      bullets: [],
    }));
    return (
      <AthleteDetailView
        athlete={athlete}
        asOf={asOf}
        series90={series90}
        recs={recs}
        factors={factors}
        day={day}
        analysis={analysis}
      />
    );
  } catch (e) {
    if (isSourceError(e)) return <SourceUnavailable />;
    throw e;
  }
}
