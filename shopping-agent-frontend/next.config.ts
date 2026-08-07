import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a minimal, self-contained server bundle in .next/standalone
  // that only includes the files needed to run `node server.js`.
  // Required for the multi-stage Dockerfile to keep the final image small.
  output: "standalone",
};

export default nextConfig;