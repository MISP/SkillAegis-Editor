/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  safelist: [
    {
      pattern: /bg-(red|green|blue|amber|purple|cyan|pink|violet)-(100|200|300|500|800|900)/, // Includes bg of all colors and shades
    },
    {
      pattern: /text-(red|green|blue|amber|purple|cyan|pink|violet)-(100|700|800|900)/, // Includes bg of all colors and shades
    },
    {
      pattern: /border-(red|green|blue|amber)-(700)/, // Includes bg of all colors and shades
    },
  ],
  theme: {
    extend: {
      transitionProperty: {
        'width': 'width'
      },
      screens: {
        '3xl': '1800px',
      },
      fontSize: {
        '2xs': '0.66rem',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
        '10xl': '104rem',
      }
    },
  },
  plugins: [
    // require('daisyui'),
  ],
  darkMode: ['selector'],
  // daisyui: {
  //   themes: false, // false: only light + dark | true: all themes | array: specific themes like this ["light", "dark", "cupcake"]
  //   darkTheme: "dark", // name of one of the included themes for dark mode
  //   base: false, // applies background color and foreground color for root element by default
  //   styled: true, // include daisyUI colors and design decisions for all components
  //   utils: false, // adds responsive and modifier utility classes
  //   prefix: "", // prefix for daisyUI classnames (components, modifiers and responsive class names. Not colors)
  //   logs: false, // Shows info about daisyUI version and used config in the console when building your CSS
  //   themeRoot: ":root", // The element that receives theme color CSS variables
  // },
}
