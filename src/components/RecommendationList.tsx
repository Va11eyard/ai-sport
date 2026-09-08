"use client";

import { useState } from "react";
import { CheckboxInput } from "@astryxdesign/core/CheckboxInput";
import { VStack } from "@astryxdesign/core/VStack";
import type { Recommendation } from "@/lib/wearables/types";

export function RecommendationList({ items }: { items: Recommendation[] }) {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  return (
    <VStack gap={3}>
      {items.map((item) => (
        <CheckboxInput
          key={item.id}
          label={item.text}
          value={!!checked[item.id]}
          onChange={(next) => setChecked((c) => ({ ...c, [item.id]: next }))}
        />
      ))}
    </VStack>
  );
}
