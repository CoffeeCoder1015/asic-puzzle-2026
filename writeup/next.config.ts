import type { NextConfig } from "next";

const configuredDebug = process.env.NEXT_PUBLIC_WRITEUP_DEBUG;
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  output: "export",
  basePath,
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
    NEXT_PUBLIC_WRITEUP_DEBUG:
      configuredDebug === "1"
        ? "1"
        : configuredDebug === undefined && process.env.NODE_ENV === "development"
          ? "1"
          : "0",
  },
  devIndicators: false,
  turbopack: { root: process.cwd() },
};

export default nextConfig;
