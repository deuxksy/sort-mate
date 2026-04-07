"""figma-to-code.py 단위 테스트"""

import pytest


def test_to_pascal_case_kebab():
    """kebab-case → PascalCase"""
    from figma_to_code import to_pascal_case
    assert to_pascal_case("home-header") == "HomeHeader"


def test_to_pascal_case_snake():
    """snake_case → PascalCase"""
    from figma_to_code import to_pascal_case
    assert to_pascal_case("waste_card_list") == "WasteCardList"


def test_to_pascal_case_spaces():
    """공백 → PascalCase"""
    from figma_to_code import to_pascal_case
    assert to_pascal_case("main screen") == "MainScreen"


def test_to_pascal_case_already_pascal():
    """이미 PascalCase인 경우"""
    from figma_to_code import to_pascal_case
    assert to_pascal_case("HomeHeader") == "HomeHeader"


def test_to_pascal_case_single_word():
    """단일 단어"""
    from figma_to_code import to_pascal_case
    assert to_pascal_case("button") == "Button"


def test_to_pascal_case_mixed_separators():
    """혼합 구분자 (kebab + space)"""
    from figma_to_code import to_pascal_case
    assert to_pascal_case("home-header item") == "HomeHeaderItem"
