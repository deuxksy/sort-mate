#!/usr/bin/env bash
set -euo pipefail

SD_DIR="$(dirname "$0")/../sd"

echo "Style Dictionary 빌드 시작..."
cd "${SD_DIR}"

# 의존성 확인
if [ ! -d "node_modules" ]; then
  echo "의존성 설치 중..."
  pnpm install --frozen-lockfile 2>/dev/null || pnpm install
fi

pnpm build

echo "✓ 빌드 완료:"
echo "  → frontend/tailwind.tokens.js"
echo "  → frontend/appsmith-theme.css"
