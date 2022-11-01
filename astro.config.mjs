import { defineConfig } from "astro/config";

// https://astro.build/config
import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  markdown: {
    syntaxHighlight: "shiki",
    shikiConfig: {
      theme: "github-light",
    },
  },
  integrations: [
    tailwind({
      config: { applyBaseStyles: false },
    }),
  ],
});
