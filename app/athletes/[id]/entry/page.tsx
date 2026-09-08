import { Heading } from "@astryxdesign/core/Heading";
import { Text } from "@astryxdesign/core/Text";
import { VStack } from "@astryxdesign/core/VStack";
import { BackNav } from "@/components/BackNav";
import { EntryForms } from "@/components/EntryForms";
import { SourceUnavailable, isSourceError } from "@/components/SourceUnavailable";
import { getAdapter } from "@/lib/wearables/getAdapter";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import Loading from "../../../loading";

export default function EntryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return (
    <Suspense fallback={<Loading />}>
      <EntryPageBody params={params} />
    </Suspense>
  );
}

async function EntryPageBody({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const adapter = getAdapter();
    const asOf = await adapter.asOf();
    const roster = await adapter.roster();
    const athlete = roster.find((a) => a.id === id);
    if (!athlete) notFound();
    return (
      <div className="page-shell max-w-[900px]">
        <VStack gap={6}>
          <VStack gap={3} hAlign="start">
            <BackNav href={`/athletes/${id}`} label="Карточка" />
            <Text type="supporting" display="block">
              {athlete.position}
            </Text>
            <Heading level={1}>{athlete.name}</Heading>
            <Text type="supporting" display="block">
              Ввод дня, лаборатории, чек-ина и питания. Scores считаются на сервере.
            </Text>
          </VStack>
          <EntryForms athleteId={id} defaultDate={asOf} />
        </VStack>
      </div>
    );
  } catch (e) {
    if (isSourceError(e)) return <SourceUnavailable />;
    throw e;
  }
}
