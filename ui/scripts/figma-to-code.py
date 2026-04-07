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


def to_pascal_case(name: str) -> str:
    """프레임명을 PascalCase로 변환.

    지원 구분자: 하이픈(-), 언더스코어(_), 공백( )
    예: home-header → HomeHeader, waste_card → WasteCard
    """
    words = re.split(r"[-_\s]+", name.strip())
    return "".join(w[:1].upper() + w[1:] for w in words if w)
