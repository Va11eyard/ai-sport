import { EmptyState } from "@astryxdesign/core/EmptyState";
import { AdapterError } from "@/src/lib/wearables/errors";

export function SourceUnavailable() {
  return (
    <div className="page-shell">
      <EmptyState
        title="Источник данных не сконфигурирован"
        description="Проверьте подключение API и адаптер физиологии."
        headingLevel={1}
      />
    </div>
  );
}

export function isSourceError(e: unknown): boolean {
  return e instanceof AdapterError && e.code === "source_not_configured";
}
