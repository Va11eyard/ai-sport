import { Card } from "@astryxdesign/core/Card";
import { Grid } from "@astryxdesign/core/Grid";
import { Heading } from "@astryxdesign/core/Heading";
import { Text } from "@astryxdesign/core/Text";
import { VStack } from "@astryxdesign/core/VStack";
import { CountUp } from "@/components/CountUp";
import type { TeamSummary } from "@/lib/wearables/types";

export function TeamHeader({
  asOf,
  summary,
}: {
  asOf: string;
  summary: TeamSummary;
}) {
  return (
    <VStack gap={5} hAlign="start">
      <VStack gap={1} hAlign="start">
        <Text type="supporting" display="block">
          Digital Athlete Twin · {asOf}
        </Text>
        <Heading level={1}>Готовность состава</Heading>
      </VStack>
      <Grid columns={{ minWidth: 120, max: 3 }} gap={3} width="100%">
        <Stat label="готовность" value={summary.meanReadiness} />
        <Stat label="флаг риска" value={summary.flaggedCount} />
        <Stat label="пропуски 7д" value={summary.missedSessionsLast7d} />
      </Grid>
    </VStack>
  );
}

function Stat({ label, value }: { label: string; value: number | null }) {
  return (
    <Card variant="muted" padding={4}>
      <Text type="supporting" display="block">
        {label}
      </Text>
      <Heading level={2} type="display-2" className="font-num">
        {value == null ? "—" : <CountUp value={value} />}
      </Heading>
    </Card>
  );
}
