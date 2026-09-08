import { Spinner } from "@astryxdesign/core/Spinner";

export default function Loading() {
  return (
    <div className="page-shell flex min-h-[50vh] items-center justify-center">
      <Spinner size="lg" label="загрузка…" />
    </div>
  );
}
