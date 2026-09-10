export function Sparkline({
  values,
  width = 88,
  height = 28,
  tone = "ready",
}: {
  values: (number | null)[];
  width?: number;
  height?: number;
  tone?: "ready" | "risk";
}) {
  const nums = values.filter((v): v is number => v != null);
  if (nums.length < 2) {
    return <svg viewBox={`0 0 ${width} ${height}`} className="h-7 w-full" />;
  }
  const min = Math.min(...nums);
  const max = Math.max(...nums);
  const span = max - min || 1;
  const step = width / (values.length - 1);
  const d = values
    .map((v, i) => {
      if (v == null) return null;
      const x = i * step;
      const y = height - ((v - min) / span) * (height - 4) - 2;
      return `${x},${y}`;
    })
    .filter((p): p is string => p != null);
  const stroke = tone === "risk" ? "var(--color-risk)" : "var(--color-ready)";
  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-7 w-full overflow-visible"
      preserveAspectRatio="none"
    >
      <polyline
        fill="none"
        stroke={stroke}
        strokeWidth="2"
        points={d.join(" ")}
      />
    </svg>
  );
}
