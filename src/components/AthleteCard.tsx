"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { Badge } from "@astryxdesign/core/Badge";
import { Text } from "@astryxdesign/core/Text";
import { ArcGauge } from "@/components/ArcGauge";
import { Sparkline } from "@/components/Sparkline";
import type { Availability } from "@/lib/athletes/availability";
import type { Athlete, DailyPhysio, RiskZone } from "@/lib/wearables/types";

const AVAIL_LABEL: Record<Availability, string> = {
  water: "на воду",
  restricted: "ограничение",
  out: "вне",
  missing: "нет данных",
};

export function AthleteCard({
  athlete,
  today,
  hrv7,
  zone,
  availability,
  why,
  featured,
}: {
  athlete: Athlete;
  today: DailyPhysio | null;
  hrv7: (number | null)[];
  zone: RiskZone;
  availability: Availability;
  why: string;
  featured?: boolean;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className="h-full"
      whileHover={reduce ? undefined : { y: -2 }}
      transition={{ duration: 0.18 }}
    >
      <Link
        href={`/athletes/${athlete.id}`}
        aria-label={`${athlete.name}, сегодня ${AVAIL_LABEL[availability]}, открыть день`}
        className={`athlete-tile${featured ? " athlete-tile--featured" : ""}`}
      >
        <span
          className={`athlete-tile__rail athlete-tile__rail--${availability}`}
          aria-hidden
        />
        <div className="athlete-tile__body">
          <Badge label={athlete.position} variant="neutral" />
          <p className="athlete-tile__name">{athlete.name}</p>
          <p className="athlete-tile__today">
            Сегодня: {AVAIL_LABEL[availability]}
          </p>
          <Text type="supporting" display="block">
            {availability === "missing" ? why : `причина: ${why}`}
          </Text>
          <div className="mt-auto flex items-end justify-between gap-3">
            <ArcGauge
              value={today?.readiness ?? null}
              size={featured ? 88 : 56}
              label="готовность"
              tone={zone === "flag" ? "risk" : "ready"}
            />
            <div className="min-w-0 flex-1 pb-1">
              <Sparkline
                values={hrv7}
                width={featured ? 140 : 88}
                tone={zone === "flag" ? "risk" : "ready"}
              />
              <Text type="supporting" display="block">
                HRV, 7 дней
              </Text>
            </div>
          </div>
          <p className="athlete-tile__open">открыть день</p>
        </div>
      </Link>
    </motion.div>
  );
}
