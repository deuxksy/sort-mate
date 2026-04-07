#!/usr/bin/env python3
"""Figma Page → React/NativeWind 컴포넌트 자동 생성 스크립트.

Usage:
    python3 ui/scripts/figma-to-code.py --page "Home"

Env:
    FIGMA_TOKEN      (필수) Figma Personal Access Token
    FIGMA_FILE_KEY   (필수) Figma 파일 키
    OPENUI_BASE      (선택) http://localhost:7878
    OPENUI_MODEL     (선택) glm-5.1
"""

import argparse
import base64
import json
import os
import re
import sys

import requests


class FigmaAPIError(Exception):
    """Figma API 호출 오류"""


def fetch_page_frames(token: str, file_key: str, page_name: str | None) -> list[dict]:
    """Figma 파일에서 지정 Page의 FRAME 노드 목록 반환.

    Args:
        token: Figma Personal Access Token
        file_key: Figma 파일 키
        page_name: Page 이름 (None이면 첫 번째 Page)

    Returns:
        [{"id": "node_id", "name": "frame_name"}, ...]

    Raises:
        FigmaAPIError: API 호출 실패 시
    """
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": token}

    resp = requests.get(url, headers=headers)

    if resp.status_code == 403:
        raise FigmaAPIError("Figma TOKEN이 만료되었거나 권한이 없습니다.")
    if resp.status_code == 404:
        raise FigmaAPIError("FIGMA_FILE_KEY를 확인하세요. 파일을 찾을 수 없습니다.")
    resp.raise_for_status()

    data = resp.json()
    pages = data.get("document", {}).get("children", [])

    if not pages:
        raise FigmaAPIError("Figma 파일에 Page가 없습니다.")

    # page_name이 None이면 첫 번째 Page 사용
    target_page = None
    for page in pages:
        if page_name is None or page.get("name") == page_name:
            target_page = page
            break

    if target_page is None:
        print(f"경고: Page '{page_name}'을(를) 찾을 수 없습니다.", file=sys.stderr)
        return []

    frames = [
        {"id": node["id"], "name": node["name"]}
        for node in target_page.get("children", [])
        if node.get("type") == "FRAME"
    ]

    if not frames:
        print(f"경고: Page '{target_page['name']}'에 FRAME이 없습니다.", file=sys.stderr)

    return frames


def export_frame_images(token: str, file_key: str, frames: list[dict]) -> list[dict]:
    """Figma 프레임을 PNG로 export하여 base64 인코딩.

    Args:
        token: Figma Personal Access Token
        file_key: Figma 파일 키
        frames: fetch_page_frames() 반환값

    Returns:
        [{"id": "...", "name": "...", "image_b64": "..."}]

    Raises:
        FigmaAPIError: API 호출 실패 시
    """
    if not frames:
        return []

    ids = ",".join(f["id"] for f in frames)
    url = f"https://api.figma.com/v1/images/{file_key}"
    headers = {"X-Figma-Token": token}
    params = {"ids": ids, "format": "png", "scale": "2"}

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 403:
        raise FigmaAPIError("Figma TOKEN이 만료되었거나 권한이 없습니다.")
    resp.raise_for_status()

    image_urls = resp.json().get("images", {})

    results = []
    for frame in frames:
        image_url = image_urls.get(frame["id"])
        if not image_url:
            print(
                f"경고: 프레임 '{frame['name']}' 이미지 export 실패, 스킵",
                file=sys.stderr,
            )
            continue

        img_resp = requests.get(image_url)
        img_resp.raise_for_status()

        results.append({
            "id": frame["id"],
            "name": frame["name"],
            "image_b64": base64.b64encode(img_resp.content).decode(),
        })

    return results


SYSTEM_PROMPT = """\
You are a React + NativeWind (Tailwind CSS for React Native) component generator.

Given a Figma frame screenshot, generate a single React component that:
1. Uses NativeWind (className prop) for styling — no inline styles
2. Is TypeScript-compatible (proper prop types via JSDoc)
3. Supports common variants (size, variant, disabled) where applicable
4. Uses only standard React Native components (View, Text, TouchableOpacity, Image, ScrollView)

Output ONLY the JSX code inside a single ```jsx code block. No explanation."""


def generate_component_code(
    openui_base: str,
    model: str,
    image_b64: str,
    frame_name: str,
    timeout: int = 30,
) -> str | None:
    """OpenUI Vision LLM으로 컴포넌트 코드 생성.

    Args:
        openui_base: OpenUI API 베이스 URL
        model: Vision LLM 모델명
        image_b64: base64 인코딩된 프레임 PNG
        frame_name: 프레임명 (프롬프트 컨텍스트용)
        timeout: 요청 타임아웃(초)

    Returns:
        JSX 코드 문자열, 실패 시 None
    """
    url = f"{openui_base}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Generate a React NativeWind component from this "
                            f"Figma frame '{frame_name}'."
                        ),
                    },
                ],
            },
        ],
        "stream": True,
    }

    try:
        resp = requests.post(
            url, json=payload, stream=True, timeout=timeout
        )
        resp.raise_for_status()
    except Exception as exc:
        print(f"오류: OpenUI 호출 실패 ({frame_name}): {exc}", file=sys.stderr)
        return None

    # SSE 스트리밍 파싱
    full_text = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        data = line[len("data: "):]
        if data.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                full_text += content
        except json.JSONDecodeError:
            continue

    # JSX 코드 블록 추출
    match = re.search(r"```jsx\s*\n(.*?)```", full_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    match = re.search(r"```(?:jsx|javascript|tsx?)\s*\n(.*?)```", full_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def save_component(output_dir: str, frame_name: str, code: str) -> str | None:
    """생성된 컴포넌트 코드를 파일로 저장.

    Args:
        output_dir: 출력 디렉터리
        frame_name: 프레임명 (PascalCase 변환 후 파일명으로 사용)
        code: JSX 코드

    Returns:
        저장된 파일 경로, 충돌 시 None
    """
    component_name = to_pascal_case(frame_name)
    filepath = os.path.join(output_dir, f"{component_name}.jsx")

    if os.path.exists(filepath):
        print(f"경고: '{filepath}' 이미 존재, 스킵", file=sys.stderr)
        return None

    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    return filepath


def save_raw_response(output_dir: str, frame_name: str, raw_text: str) -> str:
    """파싱 실패 시 원본 응답을 .raw.txt로 저장."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{to_pascal_case(frame_name)}.raw.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(raw_text)
    return filepath


def to_pascal_case(name: str) -> str:
    """프레임명을 PascalCase로 변환.

    지원 구분자: 하이픈(-), 언더스코어(_), 공백( )
    예: home-header → HomeHeader, waste_card → WasteCard
    """
    words = re.split(r"[-_\s]+", name.strip())
    return "".join(w[:1].upper() + w[1:] for w in words if w)


def main():
    """CLI 진입점."""
    parser = argparse.ArgumentParser(
        description="Figma Page → React/NativeWind 컴포넌트 자동 생성"
    )
    parser.add_argument("--page", default=None, help="대상 Figma Page 이름 (기본: 첫 번째)")
    parser.add_argument(
        "--output",
        default=os.path.join("frontend", "components", "generated"),
        help="출력 디렉터리 (기본: frontend/components/generated)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="OpenUI 타임아웃 초 (기본: 30)",
    )
    args = parser.parse_args()

    token = os.environ.get("FIGMA_TOKEN")
    file_key = os.environ.get("FIGMA_FILE_KEY")
    openui_base = os.environ.get("OPENUI_BASE", "http://localhost:7878")
    model = os.environ.get("OPENUI_MODEL", "glm-5.1")

    if not token:
        print("오류: FIGMA_TOKEN 환경변수가 필요합니다.", file=sys.stderr)
        sys.exit(1)
    if not file_key:
        print("오류: FIGMA_FILE_KEY 환경변수가 필요합니다.", file=sys.stderr)
        sys.exit(1)

    # 1. Page 내 프레임 목록 조회
    try:
        frames = fetch_page_frames(token, file_key, args.page)
    except FigmaAPIError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        sys.exit(1)

    if not frames:
        print("처리할 프레임이 없습니다.")
        return

    page_label = args.page or "(첫 번째)"
    print(f"Page '{page_label}': {len(frames)}개 프레임 발견")

    # 2. 프레임 PNG export
    try:
        exported = export_frame_images(token, file_key, frames)
    except FigmaAPIError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        sys.exit(1)

    if not exported:
        print("export된 프레임 이미지가 없습니다.")
        return

    # 3. 각 프레임 → 코드 생성 + 저장
    saved = 0
    failed = 0
    for frame in exported:
        print(f"  생성 중: {frame['name']}...", end=" ", flush=True)
        code = generate_component_code(
            openui_base, model, frame["image_b64"], frame["name"], args.timeout
        )
        if code:
            path = save_component(args.output, frame["name"], code)
            if path:
                print(f"✓ → {path}")
                saved += 1
            else:
                print("스킵 (파일 충돌)")
        else:
            print("✗ (코드 생성 실패)")
            failed += 1

    print(f"\n완료: {saved}개 생성, {failed}개 실패")


if __name__ == "__main__":
    main()
