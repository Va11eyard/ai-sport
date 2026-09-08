# UI

`lang="ru"`. Без маркетинговых заголовков. Title: «Сборная — готовность».

## Токены (`globals.css` `@theme`)

```
--color-canvas: #0A0B0D
--color-ready: #4ADE9E
--color-risk: #F2A93B
--color-muted: rgba(255,255,255,0.08)
--color-line: rgba(255,255,255,0.08)
```

Нет фиолетовых градиентов. Grain: SVG/CSS noise overlay `opacity: 0.03`, `pointer-events: none`, `z-index: 0`. Карточки `z-index: 1`. Панель риска `z-index: 20`.

Шрифт UI: `var(--font-geist)`. Числа: `font-family: var(--font-jetbrains), ui-monospace`, `font-variant-numeric: tabular-nums`, `letter-spacing: -0.04em`.

Hover карточки: `transition transform 180ms`, `hover:-translate-y-0.5` плюс Motion `whileHover={{ y: -2 }}` (один источник — Motion). Тень `0 8px 24px rgba(0,0,0,0.35)`.

Разделители: `1px solid rgb(255 255 255 / 0.08)`.

## Экран 1 — `/`

Левая колонка не центрировать. Ширина max ~1440, padding 24.

1. **Шапка сводки** (полная команда, игнорирует фильтры): средний readiness (CountUp), «флаг риска: N», «пропуски за 7 суток: N».
2. **Фильтры:** позиция (все + 5 позиций), риск (все / норма / флаг), тренд 7д HRV (все / рост / падение). Тренд: сравнение mean HRV d-7..d-1 vs d-14..d-8; нет данных → не «падение».
3. **Bento:** не 3×3. Первые 3 карточки шире (`grid-column: span 2` на xl) — худший readiness визуально крупнее. Остальные плотнее. 25 карточек.
4. Карточка: ФИО, позиция, `ArcGauge` 72–88px, sparkline HRV 7 точек, точка риска верхний правый (`ready` | `risk`). Нет данных: прочерк «нет данных», gauge пустой, не 0.
5. Пустой фильтр: «Нет атлетов по выбранным условиям.»

Сортировка: readiness desc; `null` сегодня в конце.

## Экран 2 — `/athletes/[id]`

Grid: `minmax(280px, 340px) 1fr minmax(260px, 320px)` + heatmap `grid-row` снизу на всю ширину.

- Слева: ArcGauge readiness **≥ 120px**, под ним recovery и injury risk — те же `ArcGauge` 96px (одна весовая категория). Клик по injury risk открывает панель.
- Центр: Recharts `ComposedChart` / `LineChart`, серии HRV, RHR, сон. `ReferenceArea` зоны: HRV 40–80, RHR 48–62, сон 7–9 (пример, константы в `src/lib/zones.ts`). `connectNulls={false}`. Переключатель 30 / 90 дней — searchParam `range`.
- Справа: чек-лист 2–4. Локальный check не пишет бэкенд.
- Снизу: 8 недель × 7, цвет workload 0..max → прозрачный..`#4ADE9E`, высокие дни ближе к `#F2A93B` только если intensity верхний квартиль (нагрузка, не «авария»).

## Панель риска

Модалка-drawer справа (не отдельный URL, чтобы закрытие не теряло `range`). Horizontal bars %. Плашка при флаге: «Флаг риска — рекомендуется консультация врача».

## Анимации

CountUp 600ms ease-out при маунте. ArcGauge `pathLength` 0→value. Respect `prefers-reduced-motion`.

## Desktop-first

Breakpoint: фильтры в один ряд от `lg`. Планшет: одна колонка, heatmap скролл по X. Не строить мобильный tab-bar.

## Запреты

Эмодзи, Lucide «для красоты», hero-блок с подзаголовком, стеклянные карточки одинаковой высоты, shadcn Card/Button без кастомных токенов.
