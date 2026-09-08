"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Banner } from "@astryxdesign/core/Banner";
import { Button } from "@astryxdesign/core/Button";
import { Card } from "@astryxdesign/core/Card";
import { Selector } from "@astryxdesign/core/Selector";
import { TextInput } from "@astryxdesign/core/TextInput";
import { VStack } from "@astryxdesign/core/VStack";
import { POSITIONS } from "@/lib/athletes/positions";
import { postJson } from "@/lib/entry/client";

export function NewAthleteForm() {
  const router = useRouter();
  const [lastName, setLastName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [position, setPosition] = useState<(typeof POSITIONS)[number] | "">("");
  const [terraUserId, setTerraUserId] = useState("");
  const [injury, setInjury] = useState<"yes" | "no">("no");
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const lastErr =
    lastName.trim() === "" && formError
      ? { type: "error" as const, message: "Укажите фамилию" }
      : undefined;
  const firstErr =
    firstName.trim() === "" && formError
      ? { type: "error" as const, message: "Укажите имя" }
      : undefined;
  const posErr =
    position === "" && formError
      ? { type: "error" as const, message: "Выберите позицию" }
      : undefined;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!lastName.trim() || !firstName.trim() || !position) {
      setFormError("Проверьте обязательные поля");
      return;
    }
    setBusy(true);
    setFormError(null);
    try {
      const created = await postJson<{ id: string }>("/athletes", {
        lastName: lastName.trim(),
        firstName: firstName.trim(),
        position,
        previousInjury: injury === "yes",
        ...(terraUserId.trim() ? { terraUserId: terraUserId.trim() } : {}),
      });
      router.push(`/athletes/${created.id}/entry`);
    } catch {
      setFormError("Не удалось сохранить. Проверьте API.");
      setBusy(false);
    }
  }

  return (
    <Card elevation="low" padding={5}>
      <form onSubmit={onSubmit}>
        <VStack gap={5}>
      <TextInput
        label="Фамилия"
        value={lastName}
        onChange={(v) => setLastName(v)}
        isRequired
        status={lastErr}
      />
      <TextInput
        label="Имя"
        value={firstName}
        onChange={(v) => setFirstName(v)}
        isRequired
        status={firstErr}
      />
      <Selector
        label="Позиция"
        value={position}
        onChange={(v) => setPosition((v ?? "") as typeof position)}
        options={POSITIONS.map((p) => ({ value: p, label: p }))}
        isRequired
        status={posErr}
      />
      <Selector
        label="История травмы"
        value={injury}
        onChange={(v) => setInjury((v as "yes" | "no") ?? "no")}
        options={[
          { value: "no", label: "нет" },
          { value: "yes", label: "есть" },
        ]}
      />
      <TextInput
        label="Terra user id"
        value={terraUserId}
        onChange={(v) => setTerraUserId(v)}
        isOptional
      />
      {formError && <Banner status="error" title={formError} />}
      <Button type="submit" label="Создать" variant="primary" isDisabled={busy} width="100%" />
    </VStack>
    </form>
    </Card>
  );
}