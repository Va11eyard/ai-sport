import { Badge } from "@astryxdesign/core/Badge";
import { ClickableCard } from "@astryxdesign/core/ClickableCard";
import { HStack } from "@astryxdesign/core/HStack";
import { StatusDot } from "@astryxdesign/core/StatusDot";
import { Text } from "@astryxdesign/core/Text";
import { VStack } from "@astryxdesign/core/VStack";
import { ArcGauge } from "@/components/ArcGauge";
import { Sparkline } from "@/components/Sparkline";
import type { Athlete, DailyPhysio, RiskZone } from "@/lib/wearables/types";

const ZONE_DOT: Record<RiskZone, { variant: "warning" | "success" | "neutral"; label: string }> = {
  flag: { variant: "warning", label: "флаг риска" },
  normal: { variant: "success", label: "норма" },
  missing: { variant: "neutral", label: "нет данных" },
};

export function AthleteCard({
  athlete,
  today,
  hrv7,
  zone,
  featured,
}: {
  athlete: Athlete;
  today: DailyPhysio | null;
  hrv7: (number | null)[];
  zone: RiskZone;
  featured?: boolean;
}) {
  const status = ZONE_DOT[zone];
  return (
    <ClickableCard
      href={`/athletes/${athlete.id}`}
      label={athlete.name}
      elevation="low"
      variant={zone === "flag" ? "orange" : zone === "normal" ? "green" : "default"}
      height={featured ? 200 : 148}
    >
      <VStack gap={3}>
        <HStack hAlign="between" vAlign="start">
          <Badge label={athlete.position} variant="neutral" />
          <StatusDot variant={status.variant} label={status.label} />
        </HStack>
        <Text display="block">{athlete.name}</Text>
        <HStack hAlign="between" vAlign="end" gap={3}>
          <ArcGauge
            value={today?.readiness ?? null}
            size={featured ? 72 : 56}
            label={today ? "readiness" : "нет данных"}
            tone={zone === "flag" ? "risk" : "ready"}
          />
          <div className="min-w-0 flex-1">
            <Sparkline values={hrv7} width={featured ? 120 : 88} />
          </div>
        </HStack>
      </VStack>
    </ClickableCard>
  );
}
