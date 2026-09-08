# Данные, формулы, seed

## Константы

```
SEED_KEY = "dat-waterpolo-v1"
ATHLETE_COUNT = 25
DAYS = 90
FLAG_THRESHOLD = 62          // injuryRisk >= 62 → флаг
LOW_SLEEP_H = 6.2
HRV_DROP_REL = 0.12         // падение vs медиана 14д
WORKLOAD_SPIKE_REL = 0.25  // vs среднее 7д
```

Клинические clamp (seed обязан соблюдать):

| Поле | min | max |
|------|-----|-----|
| sleepHours | 4.0 | 9.5 |
| restingHr | 42 | 78 |
| hrvRmssd | 18 | 95 |
| workload | 0 | 21 |
| recovery, readiness, injuryRisk | 0 | 100 |

## Состав

25 вымышленных ватерполистов (RU ФИО). Позиции распределить: 2 вратаря, 5 центральных, 6 подвижных, 6 крайних, 6 полусредних.

Имена фиксированы в `scripts/roster.ts`, чтобы seed был детерминирован. `previousInjury: true` у 5 атлетов (индексы 3, 7, 11, 18, 22).

Два атлета **без снимка за «сегодня»** (последняя дата ряда): id `wp-24`, `wp-25`. Карточки остаются; readiness = статус «нет данных»; в `flaggedCount` не входят.

В ряду каждого из остальных: ровно **5 несмежных дыр** в последних 90 днях (не сегодня, кроме wp-24/25). Нужно для athlete-detail edge.

«Сегодня» в моке = последняя дата сгенерированного окна, не `Date.now()`, чтобы UI и тесты совпадали. `meta.json.asOf`.

## Генерация дня (псевдокод)

Mulberry32 от `hash(SEED_KEY + athleteId + date)`.

1. Базовый сон атлета `sleep0 ∈ [6.6, 8.1]` (от id).
2. `sleepHours = clamp(sleep0 + N(0, 0.55) - 0.9 * illnessFlag)`.
3. `restingHr = clamp(52 + (7.2 - sleepHours) * 4.1 + N(0, 1.4))`.
4. `hrvRmssd = clamp(58 - (restingHr - 52) * 2.2 - (7.2 - sleepHours) * 3.0 + N(0, 3))`.
5. `workload = 0` если rest day; иначе `8..18` с недельной периодичностью (вс чаще rest).
6. Scores — детерминированные функции от (3–5) и истории 7/14 дней (ниже).
7. `missedSession = injuryRisk >= 70 && workload would-be > 0` с вероятностью 0.55 (детерминированный порог от RNG), иначе false. Не ставить пропуск при низком риске.

Проверка корреляции (тест seed): среднее `restingHr` по дням с `sleepHours < LOW_SLEEP_H` **строго больше**, чем по дням с `sleepHours >= 7.2`; HRV — строго меньше; `injuryRisk` — строго больше.

Два прогона с одним `SEED_KEY` → byte-identical JSON.

## Формулы scores (одинаковые в TS `src/lib/scores` и Python `ml/models`)

Не ML. Комментарий в Python: эвристика; класс low/medium/high как в Athlete-Injury-Risk-Analyzer (идея, не форк).

**Recovery**  
`sleepTerm = lerp(sleepHours, 4.5, 8.2) * 40`  
`hrvTerm = lerp(hrvRmssd, 25, 80) * 35`  
`rhrTerm = (1 - lerp(restingHr, 48, 72)) * 25`  
`recovery = clamp(round(sleepTerm + hrvTerm + rhrTerm))`

**Readiness**  
`recovery * 0.55 + (1 - lerp(workload, 4, 18)) * 20 + lerp(hrvRmssd, 25, 80) * 25`  
(округление 0–100)

**Injury risk**  
`sleepDebt = (1 - lerp(sleepHours, 5.0, 8.0))`  
`hrvDrop = max(0, (medianHrv14 - hrvRmssd) / max(medianHrv14, 1))`  
`spike = max(0, workload / max(meanWorkload7, 0.5) - 1)`  
`hist = 1 if previousInjury else 0`  
`raw = 28*sleepDebt + 27*clamp(hrvDrop/0.25) + 25*clamp(spike/0.4) + 20*hist`  
`injuryRisk = clamp(round(raw))`

**Флаг:** `injuryRisk >= 62`.

**Факторы (сумма 100):**  
сырьё `w = { workloadSpike: spike, sleepDebt, hrvDrop, previousInjury: hist }`  
если все 0 → равные 25/25/25/25, кроме `previousInjury=0` → 0 и 100/3 остальным.  
нормализовать, округлить до целых, остаток 100−sum добавить к наибольшему. Если `hist=0`, вклад previousInjury **ровно 0** (контракт).

## Рекомендации (2–4 пункта)

Правила, клинический тон, без диагноза:

1. Если флаг → пункт «Рекомендуется консультация врача до полной нагрузки.»
2. Если sleepHours < 6.5 → «Увеличить сон: ориентир ≥ 8 ч в ближайшие 48 ч.»
3. Если spike высокий → «Снизить тренировочную нагрузку примерно на 20–30% сегодня.»
4. Если hrvDrop → «Исключить утреннюю высокоинтенсивную работу; контроль HRV завтра.»
5. Иначе 2 нейтральных пункта про мониторинг сна и RHR.

Запрещено: «разрыв крестообразной», «вероятность травмы N%».

## Python-заглушки

`terra_adapter.py`: dataclass зеркало `DailyPhysio`; `fetch_series()` поднимает `SourceNotConfigured`.  
`kaggle_loader.py`: если нет credentials — stderr + exit 2, не скачивать.  
`injury_risk.py` / `readiness_score.py`: те же формулы, что TS; шапка с URL референсов.
