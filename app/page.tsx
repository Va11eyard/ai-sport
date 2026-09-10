import { Suspense } from "react";
import { VStack } from "@astryxdesign/core/VStack";
import { TeamBoard } from "@/components/TeamBoard";
import { TeamHeader } from "@/components/TeamHeader";
import { SourceUnavailable, isSourceError } from "@/components/SourceUnavailable";
import { countAvailability } from "@/lib/athletes/availability";
import { buildTeamRowsFromAdapter } from "@/lib/athletes/teamRows";
import { getAdapter } from "@/lib/wearables/getAdapter";
import Loading from "./loading";

export default function TeamPage() {
  return (
    <Suspense fallback={<Loading />}>
      <TeamPageBody />
    </Suspense>
  );
}

async function TeamPageBody() {
  try {
    const adapter = getAdapter();
    const asOf = await adapter.asOf();
    const summary = await adapter.teamSummary(asOf);
    const rows = await buildTeamRowsFromAdapter(adapter, asOf);
    const header = {
      ...summary,
      ...countAvailability(rows.map((r) => r.availability)),
    };
    return (
      <div className="page-shell">
        <VStack gap={6}>
          <TeamHeader
            asOf={asOf}
            summary={header}
            missingCount={rows.filter((r) => r.availability === "missing").length}
          />
          <TeamBoard rows={rows} />
        </VStack>
      </div>
    );
  } catch (e) {
    if (isSourceError(e)) return <SourceUnavailable />;
    throw e;
  }
}
