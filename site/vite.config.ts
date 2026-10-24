import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  // Served from https://pablossena.github.io/holdup/
  base: "/holdup/",
  plugins: [react()],
});
