"use client";

import { Button } from "@astryxdesign/core/Button";
import { EmptyState } from "@astryxdesign/core/EmptyState";

export default function Error({
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="page-shell">
      <EmptyState
        title="Не удалось загрузить данные"
        headingLevel={1}
        actions={<Button type="button" label="повторить" onClick={reset} />}
      />
    </div>
  );
}
