import { Grid } from "@astryxdesign/core/Grid";
import {
  MetadataList,
  MetadataListItem,
} from "@astryxdesign/core/MetadataList";
import { Text } from "@astryxdesign/core/Text";
import { VStack } from "@astryxdesign/core/VStack";
import { SectionCard } from "@/components/SectionCard";
import { burnoutIndex, nutritionTargets } from "@/lib/scores/mental";
import type { DayPayload } from "@/lib/entry/types";

export function ProfileExtras({ day }: { day: DayPayload | null }) {
  const psych = day?.psych ?? null;
  const nutrition = day?.nutrition ?? null;
  const weight = day?.extras?.weightKg ?? null;
  const targets = nutritionTargets(weight);
  const index = psych ? burnoutIndex(psych) : null;

  return (
    <Grid columns={{ minWidth: 280, max: 2 }} gap={5}>
      <SectionCard title="Питание">
        <VStack gap={4}>
          {nutrition ? (
            <MetadataList columns={2}>
              <MetadataListItem label="ккал">
                {nutrition.kcal} / {targets.kcal}
              </MetadataListItem>
              <MetadataListItem label="белок, г">
                {nutrition.proteinG} / {targets.proteinG}
              </MetadataListItem>
              <MetadataListItem label="углеводы, г">
                {nutrition.carbsG} / {targets.carbsG}
              </MetadataListItem>
              <MetadataListItem label="жиры, г">
                {nutrition.fatG} / {targets.fatG}
              </MetadataListItem>
              <MetadataListItem label="вода, л">
                {nutrition.waterL} / {targets.waterL}
              </MetadataListItem>
            </MetadataList>
          ) : (
            <Text type="supporting" display="block">
              Нет записи за этот день
            </Text>
          )}
          <Text type="supporting" display="block">
            Ориентир по массе тела, не лабораторный расчёт.
          </Text>
        </VStack>
      </SectionCard>
      <SectionCard title="Чек-ин">
        {psych && index != null ? (
          <VStack gap={4}>
            <Text type="display-2" display="block" className="font-num">
              {index}
            </Text>
            <Text type="supporting" display="block">
              индекс выгорания / 100
            </Text>
            <MetadataList columns={2}>
              <MetadataListItem label="стресс">{psych.stress}</MetadataListItem>
              <MetadataListItem label="мотивация">{psych.motivation}</MetadataListItem>
              <MetadataListItem label="тревожность">{psych.anxiety}</MetadataListItem>
              <MetadataListItem label="выгорание">{psych.burnout}</MetadataListItem>
              <MetadataListItem label="настроение">{psych.mood}</MetadataListItem>
              <MetadataListItem label="когнитивно">{psych.cognitive}</MetadataListItem>
            </MetadataList>
          </VStack>
        ) : (
          <Text type="supporting" display="block">
            Нет чек-ина за этот день
          </Text>
        )}
      </SectionCard>
    </Grid>
  );
}
