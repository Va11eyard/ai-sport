import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  reactCompiler: true,
  transpilePackages: [
    "@astryxdesign/core",
    "@astryxdesign/theme-neutral",
    "@stylexjs/stylex",
  ],
};

export default nextConfig;
