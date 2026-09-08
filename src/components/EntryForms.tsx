"use client";

import { useEffect, useState } from "react";
import { Banner } from "@astryxdesign/core/Banner";
import { Button } from "@astryxdesign/core/Button";
import { DateInput } from "@astryxdesign/core/DateInput";
import type { ISODateString } from "@astryxdesign/core/Calendar";
import { Grid } from "@astryxdesign/core/Grid";
import { Text } from "@astryxdesign/core/Text";
import { TextInput } from "@astryxdesign/core/TextInput";
import { VStack } from "@astryxdesign/core/VStack";
import { SectionCard } from "@/components/SectionCard";
import { compactNums, getDay, putJson } from "@/lib/entry/client";
import { nutritionTargets } from "@/lib/scores/mental";

function parseNum(s: string): number | undefined {
  if (s.trim() === "") return undefined;
  const n = Number(s.replace(",", "."));
  return Number.isFinite(n) ? n : NaN;
}

function parseIntField(s: string): number | undefined {
  const n = parseNum(s);
  if (n == null || Number.isNaN(n)) return n;
  return Math.round(n);
}

function statusRange(
  s: string,
  min: number,
  max: number,
  required: boolean,
  submitted: boolean,
) {
  if (!submitted && s.trim() === "") return undefined;
  if (required && s.trim() === "") {
    return { type: "error" as const, message: "Обязательное поле" };
  }
  if (s.trim() === "") return undefined;
  const n = parseNum(s);
  if (n == null || Number.isNaN(n) || n < min || n > max) {
    return { type: "error" as const, message: `Допустимо ${min}–${max}` };
  }
  return undefined;
}

export function EntryForms({
  athleteId,
  defaultDate,
}: {
  athleteId: string;
  defaultDate: string;
}) {
  const [date, setDate] = useState(defaultDate);
  const [msg, setMsg] = useState<string | null>(null);

  const [sleepHours, setSleepHours] = useState("");
  const [restingHr, setRestingHr] = useState("");
  const [hrv, setHrv] = useState("");
  const [workload, setWorkload] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [temp, setTemp] = useState("");
  const [resp, setResp] = useState("");
  const [eff, setEff] = useState("");
  const [rem, setRem] = useState("");
  const [deep, setDeep] = useState("");
  const [wake, setWake] = useState("");
  const [lat, setLat] = useState("");
  const [dist, setDist] = useState("");
  const [shots, setShots] = useState("");
  const [dayTried, setDayTried] = useState(false);

  const [hb, setHb] = useState("");
  const [vitD, setVitD] = useState("");
  const [fer, setFer] = useState("");
  const [iron, setIron] = useState("");
  const [tst, setTst] = useState("");
  const [cort, setCort] = useState("");
  const [ck, setCk] = useState("");
  const [crp, setCrp] = useState("");
  const [vo2, setVo2] = useState("");

  const [stress, setStress] = useState("5");
  const [mot, setMot] = useState("5");
  const [anx, setAnx] = useState("5");
  const [burn, setBurn] = useState("5");
  const [mood, setMood] = useState("5");
  const [cog, setCog] = useState("5");

  const [kcal, setKcal] = useState("");
  const [pro, setPro] = useState("");
  const [carb, setCarb] = useState("");
  const [fat, setFat] = useState("");
  const [water, setWater] = useState("");

  useEffect(() => {
    getDay(athleteId, date)
      .then((d) => {
        const s = d.snapshot;
        const x = d.extras;
        if (s) {
          setSleepHours(String(s.sleepHours));
          setRestingHr(String(s.restingHr));
          setHrv(String(s.hrvRmssd));
          setWorkload(String(s.workload));
        }
        if (x) {
          setWeightKg(x.weightKg != null ? String(x.weightKg) : "");
          setTemp(x.temperature != null ? String(x.temperature) : "");
          setResp(x.respRate != null ? String(x.respRate) : "");
          setEff(x.sleepEfficiency != null ? String(x.sleepEfficiency) : "");
          setRem(x.remHours != null ? String(x.remHours) : "");
          setDeep(x.deepHours != null ? String(x.deepHours) : "");
          setWake(x.awakenings != null ? String(x.awakenings) : "");
          setLat(x.sleepLatencyMin != null ? String(x.sleepLatencyMin) : "");
        }
        const t = d.training;
        if (t) {
          setDist(t.distanceM != null ? String(t.distanceM) : "");
          setShots(t.shots != null ? String(t.shots) : "");
        }
        const l = d.lab;
        if (l) {
          setHb(l.hemoglobin != null ? String(l.hemoglobin) : "");
          setVitD(l.vitaminD != null ? String(l.vitaminD) : "");
          setFer(l.ferritin != null ? String(l.ferritin) : "");
          setIron(l.iron != null ? String(l.iron) : "");
          setTst(l.testosterone != null ? String(l.testosterone) : "");
          setCort(l.cortisol != null ? String(l.cortisol) : "");
          setCk(l.ck != null ? String(l.ck) : "");
          setCrp(l.crp != null ? String(l.crp) : "");
          setVo2(l.vo2max != null ? String(l.vo2max) : "");
        }
        const p = d.psych;
        if (p) {
          setStress(String(p.stress));
          setMot(String(p.motivation));
          setAnx(String(p.anxiety));
          setBurn(String(p.burnout));
          setMood(String(p.mood));
          setCog(String(p.cognitive));
        }
        const n = d.nutrition;
        if (n) {
          setKcal(String(n.kcal));
          setPro(String(n.proteinG));
          setCarb(String(n.carbsG));
          setFat(String(n.fatG));
          setWater(String(n.waterL));
        }
      })
      .catch(() => undefined);
  }, [athleteId, date]);

  async function saveDay() {
    setDayTried(true);
    const sleep = parseNum(sleepHours);
    const hr = parseNum(restingHr);
    const h = parseNum(hrv);
    const w = parseNum(workload);
    if (
      sleep == null ||
      hr == null ||
      h == null ||
      w == null ||
      Number.isNaN(sleep) ||
      sleep < 4 ||
      sleep > 9.5
    ) {
      setMsg("Проверьте обязательные поля дня (сон 4–9.5 ч, пульс, HRV, нагрузка)");
      return;
    }
    try {
      await putJson(
        `/athletes/${athleteId}/day`,
        compactNums({
          date,
          sleepHours: sleep,
          restingHr: hr,
          hrvRmssd: h,
          workload: w,
          missedSession: false,
          weightKg: parseNum(weightKg),
          temperature: parseNum(temp),
          respRate: parseNum(resp),
          sleepEfficiency: parseNum(eff),
          remHours: parseNum(rem),
          deepHours: parseNum(deep),
          awakenings: parseIntField(wake),
          sleepLatencyMin: parseNum(lat),
          distanceM: parseNum(dist),
          shots: parseIntField(shots),
        }),
      );
      setMsg("День сохранён. Recovery / readiness / риск пересчитаны.");
    } catch (e: unknown) {
      setMsg("День не сохранён: проверьте диапазоны.");
    }
  }

  async function saveLabs() {
    try {
      await putJson(
        `/athletes/${athleteId}/labs`,
        compactNums({
          date,
          hemoglobin: parseNum(hb),
          vitaminD: parseNum(vitD),
          ferritin: parseNum(fer),
          iron: parseNum(iron),
          testosterone: parseNum(tst),
          cortisol: parseNum(cort),
          ck: parseNum(ck),
          crp: parseNum(crp),
          vo2max: parseNum(vo2),
        }),
      );
      setMsg("Лаборатория сохранена.");
    } catch {
      setMsg("Лаборатория: проверьте числа.");
    }
  }

  async function savePsych() {
    try {
      await putJson(`/athletes/${athleteId}/psych`, {
        date,
        stress: Number(stress),
        motivation: Number(mot),
        anxiety: Number(anx),
        burnout: Number(burn),
        mood: Number(mood),
        cognitive: Number(cog),
      });
      setMsg("Чек-ин сохранён.");
    } catch {
      setMsg("Чек-ин: шкалы 0–10.");
    }
  }

  async function saveNutrition() {
    try {
      await putJson(
        `/athletes/${athleteId}/nutrition`,
        compactNums({
          date,
          kcal: parseNum(kcal),
          proteinG: parseNum(pro),
          carbsG: parseNum(carb),
          fatG: parseNum(fat),
          waterL: parseNum(water),
        }),
      );
      setMsg("Питание сохранено.");
    } catch {
      setMsg("Питание: проверьте диапазоны.");
    }
  }

  const targets = nutritionTargets(parseNum(weightKg));

  return (
    <VStack gap={6}>
      <DateInput
        label="Дата"
        value={date as ISODateString}
        onChange={(v) => {
          if (v) setDate(v);
        }}
        isRequired
        format="system_date"
      />
      {msg && (
        <Banner
          status={/проверьте|не сохранён|шкалы/i.test(msg) ? "error" : "success"}
          title={msg}
        />
      )}

      <SectionCard title="День: сон, физиология, нагрузка">
        <VStack gap={4}>
        <Grid columns={{ minWidth: 220, max: 2 }} gap={4}>
          <TextInput
            label="Сон, ч"
            value={sleepHours}
            onChange={setSleepHours}
            isRequired
            status={statusRange(sleepHours, 4, 9.5, true, dayTried)}
          />
          <TextInput
            label="Пульс покоя"
            value={restingHr}
            onChange={setRestingHr}
            isRequired
            status={statusRange(restingHr, 42, 78, true, dayTried)}
          />
          <TextInput
            label="HRV RMSSD"
            value={hrv}
            onChange={setHrv}
            isRequired
            status={statusRange(hrv, 18, 95, true, dayTried)}
          />
          <TextInput
            label="Нагрузка (0–21)"
            value={workload}
            onChange={setWorkload}
            isRequired
            status={statusRange(workload, 0, 21, true, dayTried)}
          />
          <TextInput label="Вес, кг" value={weightKg} onChange={setWeightKg} isOptional />
          <TextInput label="Температура" value={temp} onChange={setTemp} isOptional />
          <TextInput label="ЧД" value={resp} onChange={setResp} isOptional />
          <TextInput label="Эффективность сна %" value={eff} onChange={setEff} isOptional />
          <TextInput label="REM, ч" value={rem} onChange={setRem} isOptional />
          <TextInput label="Deep, ч" value={deep} onChange={setDeep} isOptional />
          <TextInput label="Пробуждения" value={wake} onChange={setWake} isOptional />
          <TextInput label="Засыпание, мин" value={lat} onChange={setLat} isOptional />
          <TextInput label="Дистанция, м" value={dist} onChange={setDist} isOptional />
          <TextInput label="Броски" value={shots} onChange={setShots} isOptional />
        </Grid>
        <Button label="Сохранить день" variant="primary" onClick={saveDay} width="100%" />
        </VStack>
      </SectionCard>

      <SectionCard title="Лаборатория">
        <VStack gap={4}>
        <Grid columns={{ minWidth: 220, max: 2 }} gap={4}>
          <TextInput label="Гемоглобин" value={hb} onChange={setHb} isOptional />
          <TextInput label="Витамин D" value={vitD} onChange={setVitD} isOptional />
          <TextInput label="Ферритин" value={fer} onChange={setFer} isOptional />
          <TextInput label="Железо" value={iron} onChange={setIron} isOptional />
          <TextInput label="Тестостерон" value={tst} onChange={setTst} isOptional />
          <TextInput label="Кортизол" value={cort} onChange={setCort} isOptional />
          <TextInput label="CK" value={ck} onChange={setCk} isOptional />
          <TextInput label="CRP" value={crp} onChange={setCrp} isOptional />
          <TextInput label="VO₂max" value={vo2} onChange={setVo2} isOptional />
        </Grid>
        <Button label="Сохранить лабораторию" onClick={saveLabs} width="100%" />
        </VStack>
      </SectionCard>

      <SectionCard title="Психологический чек-ин (0–10)">
        <VStack gap={4}>
        <Grid columns={{ minWidth: 220, max: 2 }} gap={4}>
          <TextInput label="Стресс" value={stress} onChange={setStress} />
          <TextInput label="Мотивация" value={mot} onChange={setMot} />
          <TextInput label="Тревожность" value={anx} onChange={setAnx} />
          <TextInput label="Выгорание" value={burn} onChange={setBurn} />
          <TextInput label="Настроение" value={mood} onChange={setMood} />
          <TextInput label="Когнитивная готовность" value={cog} onChange={setCog} />
        </Grid>
        <Button label="Сохранить чек-ин" onClick={savePsych} width="100%" />
        </VStack>
      </SectionCard>

      <SectionCard title="Питание за день">
        <VStack gap={4}>
        <Text type="supporting" display="block">
          Ориентир: {targets.kcal} ккал · белок {targets.proteinG} г · углеводы{" "}
          {targets.carbsG} г · жиры {targets.fatG} г · вода {targets.waterL} л
        </Text>
        <Grid columns={{ minWidth: 220, max: 2 }} gap={4}>
          <TextInput label="ккал" value={kcal} onChange={setKcal} isRequired />
          <TextInput label="Белок, г" value={pro} onChange={setPro} isRequired />
          <TextInput label="Углеводы, г" value={carb} onChange={setCarb} isRequired />
          <TextInput label="Жиры, г" value={fat} onChange={setFat} isRequired />
          <TextInput label="Вода, л" value={water} onChange={setWater} isRequired />
        </Grid>
        <Button label="Сохранить питание" onClick={saveNutrition} width="100%" />
        </VStack>
      </SectionCard>
    </VStack>
  );
}