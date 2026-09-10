"use client";

import { useMemo, useState } from "react";
import { Button } from "@astryxdesign/core/Button";
import { Badge } from "@astryxdesign/core/Badge";
import { Heading } from "@astryxdesign/core/Heading";
import { HStack } from "@astryxdesign/core/HStack";
import { Icon } from "@astryxdesign/core/Icon";
import { SegmentedControl, SegmentedControlItem } from "@astryxdesign/core/SegmentedControl";
import { Text } from "@astryxdesign/core/Text";
import { VStack } from "@astryxdesign/core/VStack";
import { ArrowLeftIcon } from "@heroicons/react/24/outline";
import { ArcGauge } from "@/components/ArcGauge";
import { AnalysisPanel } from "@/components/AnalysisPanel";
import { InjuryPanel } from "@/components/InjuryPanel";
import { LoadHeatmap } from "@/components/LoadHeatmap";
import { PhysioChart } from "@/components/PhysioChart";
import { ProfileExtras } from "@/components/ProfileExtras";
import { RecommendationList } from "@/components/RecommendationList";
import { SectionCard } from "@/components/SectionCard";
import { addDays } from "@/lib/scores/math";
import { FLAG_THRESHOLD } from "@/lib/scores/ranges";
import type { DayPayload } from "@/lib/entry/types";
import type {
  Athlete,
  DailyPhysio,
  DayAnalysis,
  InjuryFactors,
  Recommendation,
} from "@/lib/wearables/types";

export function AthleteDetailView({
  athlete,
  asOf,
  series90,
  recs,
  factors,
  day,
  analysis,
}: {
  athlete: Athlete;
  asOf: string;
  series90: (DailyPhysio | null)[];
  recs: Recommendation[];
  factors: InjuryFactors;
  day: DayPayload | null;
  analysis: DayAnalysis;
}) {
  const [range, setRange] = useState<30 | 90>(30);
  const [panel, setPanel] = useState(false);
  const from30 = addDays(asOf, -29);
  const shown = useMemo(() => {
    if (range === 90) return series90;
    const start = series90.findIndex((s) => (s?.date ?? "") >= from30);
    return start >= 0 ? series90.slice(start) : series90.slice(-30);
  }, [range, series90, from30]);
  const today = series90.find((s) => s?.date === asOf) ?? null;
  const tone = today && today.injuryRisk >= FLAG_THRESHOLD ? "risk" : "ready";

  return (
    <div className="page-shell">
      <VStack gap={6}>
        <VStack gap={3} hAlign="start">
          <Button
            href="/"
            variant="ghost"
            size="lg"
            className="min-h-11"
            label="К составу на сегодня"
            icon={<Icon icon={ArrowLeftIcon} size="sm" />}
          />
          <HStack hAlign="start" vAlign="center" gap={3} wrap="wrap">
            <Badge label={athlete.position} variant="neutral" />
            <Text type="supporting">
              {athlete.terraUserId ? "источник: Terra" : "источник: ручной ввод"}
            </Text>
          </HStack>
          <Heading level={1}>{athlete.name}</Heading>
          <Button
            href={`/athletes/${athlete.id}/entry`}
            label="Внести данные"
            size="lg"
            variant="primary"
            className="min-h-11"
          />
        </VStack>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(240px,320px)_1fr_280px] xl:gap-8">
          <VStack gap={5} hAlign="start">
            <HStack hAlign="between" vAlign="end" gap={4} wrap="wrap">
              <ArcGauge
                value={today?.readiness ?? null}
                size={120}
                label="готовность"
                tone={tone}
              />
              <ArcGauge
                value={today?.recovery ?? null}
                size={72}
                label="восстановление"
                tone="recover"
              />
              <ArcGauge
                value={today?.injuryRisk ?? null}
                size={72}
                label="риск"
                tone="risk"
              />
            </HStack>
            <Button
              type="button"
              variant="secondary"
              size="lg"
              className="min-h-11"
              label="Разбивка риска"
              onClick={() => setPanel(true)}
            />
          </VStack>

          <SectionCard title="Физиология">
            <VStack gap={4}>
              <SegmentedControl
                value={String(range)}
                onChange={(v) => setRange(Number(v) as 30 | 90)}
                label="Период графика"
              >
                <SegmentedControlItem value="30" label="30 дней" />
                <SegmentedControlItem value="90" label="90 дней" />
              </SegmentedControl>
              <PhysioChart series={shown} />
            </VStack>
          </SectionCard>

          <SectionCard title="На сегодня">
            <RecommendationList items={recs} />
          </SectionCard>
        </div>

        <AnalysisPanel analysis={analysis} />

        <ProfileExtras day={day} />

        <SectionCard title="нагрузка · 8 недель">
          <LoadHeatmap series={series90} asOf={asOf} />
        </SectionCard>
      </VStack>

      <div className="relative z-20">
      <InjuryPanel
        open={panel}
        factors={factors}
        injuryRisk={today?.injuryRisk ?? null}
        onClose={() => setPanel(false)}
      />
      </div>
    </div>
  );
}
