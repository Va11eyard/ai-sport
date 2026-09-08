"use client";

import { Banner } from "@astryxdesign/core/Banner";
import { BottomSheet } from "@astryxdesign/core/BottomSheet";
import { ProgressBar } from "@astryxdesign/core/ProgressBar";
import { VStack } from "@astryxdesign/core/VStack";
import { FLAG_THRESHOLD } from "@/lib/scores/ranges";
import type { InjuryFactors } from "@/lib/wearables/types";

const LABELS: { key: keyof InjuryFactors; label: string }[] = [
  { key: "workloadSpike", label: "скачок нагрузки" },
  { key: "sleepDebt", label: "недосып" },
  { key: "hrvDrop", label: "падение HRV" },
  { key: "previousInjury", label: "история травмы" },
];

export function InjuryPanel({
  open,
  factors,
  injuryRisk,
  onClose,
}: {
  open: boolean;
  factors: InjuryFactors;
  injuryRisk: number | null;
  onClose: () => void;
}) {
  const flagged = injuryRisk != null && injuryRisk >= FLAG_THRESHOLD;
  return (
    <BottomSheet
      isOpen={open}
      onOpenChange={(isOpen) => {
        if (!isOpen) onClose();
      }}
      label="Факторы риска"
      purpose="info"
    >
      <VStack gap={5}>
        {flagged && (
          <Banner
            status="warning"
            title="Флаг риска"
            description="рекомендуется консультация врача"
          />
        )}
        {LABELS.map((row) => (
          <ProgressBar
            key={row.key}
            label={row.label}
            value={factors[row.key]}
            max={100}
            variant="warning"
            hasValueLabel
          />
        ))}
      </VStack>
    </BottomSheet>
  );
}
