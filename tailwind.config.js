const plugin = require("tailwindcss/plugin");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  theme: {
    extend: {
      width: {
        "1/5": "20%",
        "4/5": "80%",
      },
    },
  },
};
