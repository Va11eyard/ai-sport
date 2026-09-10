import { Heading } from "@astryxdesign/core/Heading";
import { CountUp } from "@/components/CountUp";
import type { TeamSummary } from "@/lib/wearables/types";

export function TeamHeader({
  asOf,
  summary,
  missingCount,
}: {
  asOf: string;
  summary: TeamSummary;
  missingCount: number;
}) {
  return (
    <header className="today-brief">
      <p className="today-brief__kicker">
        Сегодня · <span className="font-num">{asOf}</span>
      </p>
      <Heading level={1} className="today-brief__title">
        Кто на воду
      </Heading>
      <p className="today-brief__lead">
        Сначала список внимания — нет снимка, вне состава или ограничение. Затем
        те, кто может полную сессию. Карточка открывает день атлета.
      </p>
      <ul className="today-brief__decisions">
        <li>
          <span className="today-brief__n font-num today-brief__n--water">
            <CountUp value={summary.availableCount} />
          </span>
          <span className="today-brief__label">на воду</span>
          <span className="today-brief__hint">полная сессия</span>
        </li>
        <li>
          <span className="today-brief__n font-num today-brief__n--restricted">
            <CountUp value={summary.restrictedCount} />
          </span>
          <span className="today-brief__label">ограничение</span>
          <span className="today-brief__hint">снизить нагрузку</span>
        </li>
        <li>
          <span className="today-brief__n font-num today-brief__n--out">
            <CountUp value={summary.outCount} />
          </span>
          <span className="today-brief__label">вне</span>
          <span className="today-brief__hint">не в воде сегодня</span>
        </li>
        <li>
          <span className="today-brief__n font-num">
            <CountUp value={missingCount} />
          </span>
          <span className="today-brief__label">нет снимка</span>
          <span className="today-brief__hint">не считать нулём</span>
        </li>
      </ul>
      <p className="today-brief__meta">
        средняя готовность{" "}
        <strong className="font-num">
          {summary.meanReadiness == null ? "—" : <CountUp value={summary.meanReadiness} />}
        </strong>
        <span className="today-brief__dot" aria-hidden>
          ·
        </span>
        флаг риска{" "}
        <strong className="font-num">
          <CountUp value={summary.flaggedCount} />
        </strong>
        <span className="today-brief__dot" aria-hidden>
          ·
        </span>
        пропуски за 7 суток{" "}
        <strong className="font-num">
          <CountUp value={summary.missedSessionsLast7d} />
        </strong>
      </p>
    </header>
  );
}
