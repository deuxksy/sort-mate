const path = require("path");
const StyleDictionary = require("style-dictionary").default;

/** camelCase 변환: ["color","primary","default"] → "colorPrimaryDefault" */
const toCamelCase = (parts) =>
  parts
    .map((p, i) =>
      i === 0 ? p.toLowerCase() : p.charAt(0).toUpperCase() + p.slice(1),
    )
    .join("");

// v4: formatter → format 속성명 변경
StyleDictionary.registerFormat({
  name: "javascript/es6Camel",
  format: function ({ dictionary }) {
    return dictionary.allTokens
      .map((t) => `export const ${toCamelCase(t.path)} = "${t.value}";`)
      .join("\n") + "\n";
  },
});

module.exports = {
  source: [path.join(__dirname, "../tokens/**/*.json")],
  platforms: {
    tailwind: {
      transformGroup: "css",
      buildPath: path.join(__dirname, "../../frontend/"),
      files: [
        {
          destination: "tailwind.tokens.js",
          format: "javascript/es6Camel",
        },
      ],
    },
    appsmith: {
      transformGroup: "css",
      buildPath: path.join(__dirname, "../../frontend/"),
      files: [
        {
          destination: "appsmith-theme.css",
          format: "css/variables",
          options: {
            outputReferences: true,
          },
        },
      ],
    },
  },
};
