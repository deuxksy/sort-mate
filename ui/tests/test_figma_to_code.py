"""figma-to-code.py 단위 테스트"""

import pytest
from unittest.mock import patch, MagicMock


def _make_file_response(pages):
    """Figma GET /v1/files/{key} 응답 mock 생성"""
    return {
        "document": {
            "children": [
                {"name": name, "type": "CANVAS", "children": frames}
                for name, frames in pages.items()
            ]
        }
    }


class TestFetchPageFrames:
    """Figma 파일 구조에서 Page 내 frame 노드 추출"""

    def test_returns_frame_ids_and_names(self):
        from figma_to_code import fetch_page_frames

        resp = _make_file_response({
            "Home": [
                {"id": "1:2", "name": "home-header", "type": "FRAME"},
                {"id": "1:3", "name": "waste-card", "type": "FRAME"},
            ]
        })
        with patch("figma_to_code.requests.get") as mock:
            mock.return_value = MagicMock(status_code=200, json=lambda: resp)
            result = fetch_page_frames("t", "k", "Home")

        assert result == [{"id": "1:2", "name": "home-header"}, {"id": "1:3", "name": "waste-card"}]

    def test_skips_non_frame_nodes(self):
        from figma_to_code import fetch_page_frames

        resp = _make_file_response({
            "Home": [
                {"id": "1:2", "name": "header", "type": "FRAME"},
                {"id": "1:3", "name": "group1", "type": "GROUP"},
                {"id": "1:4", "name": "text1", "type": "TEXT"},
            ]
        })
        with patch("figma_to_code.requests.get") as mock:
            mock.return_value = MagicMock(status_code=200, json=lambda: resp)
            result = fetch_page_frames("t", "k", "Home")

        assert len(result) == 1
        assert result[0]["name"] == "header"

    def test_page_not_found_returns_empty(self):
        from figma_to_code import fetch_page_frames

        resp = _make_file_response({"Other": []})
        with patch("figma_to_code.requests.get") as mock, patch("sys.stderr"):
            mock.return_value = MagicMock(status_code=200, json=lambda: resp)
            result = fetch_page_frames("t", "k", "Missing")

        assert result == []

    def test_default_page_uses_first(self):
        from figma_to_code import fetch_page_frames

        resp = _make_file_response({
            "Home": [{"id": "1:1", "name": "hero", "type": "FRAME"}],
            "Detail": [],
        })
        with patch("figma_to_code.requests.get") as mock:
            mock.return_value = MagicMock(status_code=200, json=lambda: resp)
            result = fetch_page_frames("t", "k", None)

        assert result == [{"id": "1:1", "name": "hero"}]

    def test_api_403_raises(self):
        from figma_to_code import fetch_page_frames, FigmaAPIError

        with patch("figma_to_code.requests.get") as mock:
            mock.return_value = MagicMock(status_code=403)
            with pytest.raises(FigmaAPIError, match="TOKEN"):
                fetch_page_frames("bad", "k", "Home")

    def test_api_404_raises(self):
        from figma_to_code import fetch_page_frames, FigmaAPIError

        with patch("figma_to_code.requests.get") as mock:
            mock.return_value = MagicMock(status_code=404)
            with pytest.raises(FigmaAPIError, match="FILE_KEY"):
                fetch_page_frames("t", "bad", "Home")


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
