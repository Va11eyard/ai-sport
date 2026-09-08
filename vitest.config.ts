import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: {
    environment: "node",
    coverage: {
      provider: "v8",
      include: [
        "src/lib/scores/**/*.ts",
        "src/lib/synthetic/**/*.ts",
        "src/lib/wearables/**/*.ts",
        "src/lib/athletes/roster.ts",
        "src/lib/terra/**/*.ts",
        "src/lib/analysis/**/*.ts",
      ],
      exclude: [
        "**/*.test.ts",
        "src/lib/wearables/http-adapter.ts",
        "src/lib/wearables/index.ts",
        "src/lib/wearables/queries.ts",
        "src/lib/wearables/terra-adapter.ts",
      ],
      thresholds: { lines: 80, functions: 80, statements: 80, branches: 70 },
    },
  },
  resolve: {
    alias: { "@": path.resolve(__dirname, ".") },
  },
});