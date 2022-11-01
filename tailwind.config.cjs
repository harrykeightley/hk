const disabledCss = {
  "code::before": false,
  "code::after": false,
  "blockquote p:first-of-type::before": false,
  "blockquote p:last-of-type::after": false,
  pre: false,
  code: false,
  "pre code": false,
  "code::before": false,
  "code::after": false,
};

const sizes = ["default", "DEFAULT", "sm", "lg", "xl", "2xl"];
const typography = sizes.reduce(
  (result, size) => ({
    ...result,
    [size]: { css: disabledCss },
  }),
  {}
);

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {
      typography,
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
