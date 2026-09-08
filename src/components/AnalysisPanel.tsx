import { Banner } from "@astryxdesign/core/Banner";
import { List, ListItem } from "@astryxdesign/core/List";
import { SectionCard } from "@/components/SectionCard";
import type { DayAnalysis } from "@/lib/wearables/types";

const COPY: Record<DayAnalysis["status"], string | null> = {
  ok: null,
  unconfigured: "анализ недоступен",
  no_snapshot: "нет данных за день",
  upstream_error: "не удалось получить анализ",
  invalid_output: "не удалось получить анализ",
};

export function AnalysisPanel({ analysis }: { analysis: DayAnalysis }) {
  const msg = COPY[analysis.status];
  return (
    <SectionCard title="ИИ-разбор">
      <div aria-live="polite">
        {msg ? (
          <Banner status="info" title={msg} />
        ) : (
          <List density="spacious" listStyle="disc">
            {analysis.bullets.map((b) => (
              <ListItem key={b} label={b} />
            ))}
          </List>
        )}
      </div>
    </SectionCard>
  );
}
