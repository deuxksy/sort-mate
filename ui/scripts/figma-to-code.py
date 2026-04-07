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


def to_pascal_case(name: str) -> str:
    """프레임명을 PascalCase로 변환.

    지원 구분자: 하이픈(-), 언더스코어(_), 공백( )
    예: home-header → HomeHeader, waste_card → WasteCard
    """
    words = re.split(r"[-_\s]+", name.strip())
    return "".join(w[:1].upper() + w[1:] for w in words if w)
