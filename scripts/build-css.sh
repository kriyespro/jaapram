#!/usr/bin/env bash
set -euo pipefail
# Regenerates static/css/app.css: purged Tailwind utilities (only classes actually
# used in templates, not the full framework) + our hand-written base.css, combined
# into one file so the browser makes a single CSS request instead of two.
#
# Run this after changing base.css, or after adding/removing Tailwind utility
# classes in any template — Tailwind's purge only keeps classes it can find by
# scanning template text, so a class added to a template won't appear in the
# built CSS until this script runs again.
#
# Requires node/npm.

cd "$(dirname "$0")/.."

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

cat > "$TMP_DIR/input.css" <<'CSS'
@tailwind base;
@tailwind components;
@tailwind utilities;
CSS

cat > "$TMP_DIR/tailwind.config.js" <<JS
module.exports = {
  purge: {
    enabled: true,
    content: ['$(pwd)/ram_naam_jaap/templates/**/*.html'],
  },
  darkMode: false,
  theme: { extend: {} },
  variants: {},
  plugins: [],
}
JS

( cd "$TMP_DIR" && npm init -y >/dev/null 2>&1 && npm install tailwindcss@2.2.19 >/dev/null 2>&1 )
( cd "$TMP_DIR" && npx tailwindcss -c tailwind.config.js -i input.css -o tailwind.css --minify )

cat "$TMP_DIR/tailwind.css" ram_naam_jaap/static/css/base.css > ram_naam_jaap/static/css/app.css
echo "Wrote ram_naam_jaap/static/css/app.css ($(wc -c < ram_naam_jaap/static/css/app.css) bytes)"
