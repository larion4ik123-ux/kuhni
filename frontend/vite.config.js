import { defineConfig } from "vite";

const repositoryBase = process.env.GITHUB_REPOSITORY
  ? `/${process.env.GITHUB_REPOSITORY.split("/")[1]}/`
  : process.env.VITE_BASE_PATH || "/";

export default defineConfig({
  base: repositoryBase,
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: false,
  },
});
