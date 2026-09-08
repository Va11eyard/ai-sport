import { EmptyState } from "@astryxdesign/core/EmptyState";

export default function NotFound() {
  return (
    <div className="page-shell">
      <EmptyState title="Атлет не найден" headingLevel={1} />
    </div>
  );
}
