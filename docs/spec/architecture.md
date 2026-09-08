# Архитектура

## Потоки

```
TeamOverview (RSC)
  → getWearableAdapter().roster() + teamSummary() + today snapshots
AthleteDetail (RSC + client charts)
  → athleteSeries(id, from, to)
  → todayRecommendations(id)
  → injuryFactorBreakdown(id)
TerraWearableAdapter ──(no credentials)──► AdapterError source_not_configured
MockWearableAdapter ──► data/synthetic/*.json  (только внутри адаптера)
```

UI, страницы и компоненты **не** импортируют `data/synthetic`.

## Дерево файлов (цель после Gherkin)

```
app/
  layout.tsx                 # lang=ru, Geist + JetBrains_Mono, grain overlay
  globals.css              # Tailwind v4 @theme tokens
  page.tsx                 # Team Overview (/)
  loading.tsx
  error.tsx
  not-found.tsx
  athletes/[id]/
    page.tsx               # async params
    loading.tsx
  api/health/route.ts      # GET { ok: true }

src/
  components/
    ArcGauge.tsx           # client: SVG arc, Motion fill
    ScoreCluster.tsx      # readiness + recovery + risk
    AthleteCard.tsx
    TeamBento.tsx
    TeamFilters.tsx
    TeamSummaryBar.tsx
    HrvSparkline.tsx
    PhysioChart.tsx       # Recharts 3, 30/90d
    LoadHeatmap.tsx       # 8 weeks
    RecommendationList.tsx
    InjuryBreakdownPanel.tsx
    CountUp.tsx
    SourceStatus.tsx     # Terra unconfigured
  lib/
    wearables/
      types.ts
      errors.ts
      interface.ts
      mock-adapter.ts
      terra-adapter.ts
      index.ts             # factory from WEARABLE_SOURCE
    scores/
      readiness.ts
      recovery.ts
      injury-risk.ts
      recommendations.ts
      factors.ts
    athletes/
      positions.ts
    format.ts
  styles/
    grain.css

data/synthetic/
  athletes.json
  snapshots.json           # или parquet позже; MVP = JSON
  meta.json                # seed key, generatedAt, ranges

data/adapters/
  terra_adapter.py         # NotImplemented / credentials check
  kaggle_loader.py         # exit 2 если нет ~/.kaggle

ml/models/
  injury_risk.py
  readiness_score.py

scripts/
  seed_synthetic.ts
```

## WearableAdapter

```ts
export type IsoDate = string // YYYY-MM-DD

export interface DailyPhysio {
  athleteId: string
  date: IsoDate
  sleepHours: number
  restingHr: number
  hrvRmssd: number
  workload: number
  recovery: number
  readiness: number
  injuryRisk: number
  missedSession: boolean
}

export interface Athlete {
  id: string
  lastName: string
  firstName: string
  position: WaterPoloPosition
  previousInjury: boolean
}

export type WaterPoloPosition =
  | "вратарь"
  | "центральный"
  | "подвижный"
  | "крайний"
  | "полусредний"

export interface TeamSummary {
  athleteCount: number
  meanReadiness: number | null // только атлеты со снимком сегодня
  flaggedCount: number         // injuryRisk >= FLAG_THRESHOLD и есть снимок
  missedSessionsLast7d: number
}

export interface InjuryFactors {
  workloadSpike: number
  sleepDebt: number
  hrvDrop: number
  previousInjury: number
  // сумма === 100 после округления (см. data-and-scores.md)
}

export interface Recommendation {
  id: string
  text: string
  checked: false // UI чек-лист локальный, не persist в MVP
}

export class AdapterError extends Error {
  constructor(
    readonly code: "source_not_configured" | "not_found" | "invalid_snapshot",
    message: string,
  ) { super(message) }
}

export interface WearableAdapter {
  roster(): Promise<Athlete[]>
  teamSummary(today: IsoDate): Promise<TeamSummary>
  todaySnapshot(athleteId: string, today: IsoDate): Promise<DailyPhysio | null>
  athleteSeries(athleteId: string, from: IsoDate, to: IsoDate): Promise<(DailyPhysio | null)[]>
  // ряд календарно непрерывный: дыры = null, не нули
  todayRecommendations(athleteId: string, today: IsoDate): Promise<Recommendation[]>
  injuryFactorBreakdown(athleteId: string, today: IsoDate): Promise<InjuryFactors>
}
```

`WEARABLE_SOURCE=mock|terra` (default `mock`). Terra без env `TERRA_API_KEY` → `AdapterError("source_not_configured")`.

## RSC vs client

| Server | Client (`"use client"`) |
|--------|--------------------------|
| pages, layout, загрузка адаптера | ArcGauge, CountUp, hover карточек, фильтры (URL searchParams можно на сервере) |
| фильтры: `?position=&risk=&trend=` — предпочтительно RSC + `<form>` / `Link` | Motion hover `translateY(-2px)` |
| | Recharts, heatmap hit-areas |

Фильтры пустой выборки: сетка пустая, шапка всё ещё `teamSummary` **полной** команды (контракт team-overview).
