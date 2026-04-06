#!/usr/bin/env bash
set -euo pipefail

# Figma Variables API → tokens.json 동기화
# 사용법: FIGMA_TOKEN=<pat> FIGMA_FILE_KEY=<file-key> ./figma-sync.sh

FIGMA_API="https://api.figma.com/v1"
TOKEN="${FIGMA_TOKEN:?FIGMA_TOKEN 환경변수가 필요합니다}"
FILE_KEY="${FIGMA_FILE_KEY:?FIGMA_FILE_KEY 환경변수가 필요합니다}"
OUTPUT_DIR="$(dirname "$0")/../tokens"
OUTPUT="${OUTPUT_DIR}/tokens.json"

mkdir -p "${OUTPUT_DIR}"

echo "Figma Variables 조회 중... (file: ${FILE_KEY})"

# Figma Variables API 호출
RESPONSE=$(curl -sf \
  -H "X-Figma-Token: ${TOKEN}" \
  "${FIGMA_API}/files/${FILE_KEY}/variables/local") || {
    echo "ERROR: Figma API 호출 실패. TOKEN과 FILE_KEY를 확인하세요." >&2
    exit 1
  }

# Variables → Design Tokens 형식 변환 (python 사용)
python3 - "$RESPONSE" <<'PYEOF' > "${OUTPUT}"
import sys, json

data = json.load(sys.stdin)
tokens = {}

variables = data.get("variables", {})
for var_id, var in variables.items():
    name = var["name"].replace("/", ".")
    var_type = var.get("variableType", "other")
    resolved_type = var.get("resolvedType", "string")

    # 모드별 값 (light/dark 등) → 첫 번째 모드 값 사용
    values_by_mode = var.get("valuesByMode", {})
    value = next(iter(values_by_mode.values()), None)

    if value is None:
        continue

    # 그룹 분리 (color.primary.DEFAULT 형태)
    parts = name.split(".")
    current = tokens
    for part in parts[:-1]:
        current = current.setdefault(part, {})

    token_type = {
        "COLOR": "color",
        "FLOAT": "number",
        "STRING": "string",
        "BOOLEAN": "boolean",
    }.get(resolved_type, "other")

    current[parts[-1]] = {
        "value": str(value) if not isinstance(value, (int, float)) else value,
        "type": token_type,
    }

json.dump(tokens, sys.stdout, indent=2)
PYEOF

echo "✓ tokens.json 저장 완료: ${OUTPUT}"
