import { FLAG_THRESHOLD, WORKLOAD_SPIKE_REL } from "./constants";

export type Recommendation = {
  id: string;
  text: string;
  checked: false;
};

export function todayRecommendations(args: {
  injuryRisk: number;
  sleepHours: number;
  spike: number;
  hrvDrop: number;
  burnoutIndex?: number;
}): Recommendation[] {
  const items: Recommendation[] = [];
  if (args.injuryRisk >= FLAG_THRESHOLD) {
    items.push({
      id: "physician",
      text: "Рекомендуется консультация врача до полной нагрузки.",
      checked: false,
    });
  }
  if (args.burnoutIndex != null && args.burnoutIndex >= 65) {
    items.push({
      id: "mental",
      text: "Снизить интенсивность; консультация спортивного психолога; дыхательные практики.",
      checked: false,
    });
  }
  if (args.sleepHours < 6.5) {
    items.push({
      id: "sleep",
      text: "Увеличить сон: ориентир ≥ 8 ч в ближайшие 48 ч.",
      checked: false,
    });
  }
  if (args.spike >= WORKLOAD_SPIKE_REL) {
    items.push({
      id: "load",
      text: "Снизить тренировочную нагрузку примерно на 20–30% сегодня.",
      checked: false,
    });
  }
  if (args.hrvDrop >= 0.12) {
    items.push({
      id: "hrv",
      text: "Исключить утреннюю высокоинтенсивную работу; контроль HRV завтра.",
      checked: false,
    });
  }
  if (items.length < 2) {
    items.push({
      id: "sleep-monitor",
      text: "Контроль продолжительности сна в ближайшие двое суток.",
      checked: false,
    });
    items.push({
      id: "rhr",
      text: "Сверить пульс покоя с медианой 7 дней; без расширения объёма.",
      checked: false,
    });
  }
  return items.slice(0, 4);
}