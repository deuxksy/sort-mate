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


class TestExportFrameImages:
    """Figma 프레임 PNG export + base64 인코딩"""

    def test_downloads_and_returns_base64(self):
        from figma_to_code import export_frame_images

        frames = [{"id": "1:2", "name": "home-header"}]
        png_bytes = b"\x89PNG\r\n\x1a\nfake"

        images_resp = MagicMock(status_code=200)
        images_resp.json.return_value = {"images": {"1:2": "https://cdn.figma.com/img.png"}}

        img_resp = MagicMock(status_code=200, content=png_bytes)
        img_resp.raise_for_status = MagicMock()

        def mock_get(url, **kwargs):
            if "images" in url and "cdn" not in url:
                return images_resp
            return img_resp

        with patch("figma_to_code.requests.get", side_effect=mock_get):
            result = export_frame_images("t", "k", frames)

        assert len(result) == 1
        assert result[0]["id"] == "1:2"
        assert result[0]["name"] == "home-header"
        import base64
        assert result[0]["image_b64"] == base64.b64encode(png_bytes).decode()

    def test_missing_image_skipped(self):
        from figma_to_code import export_frame_images

        frames = [
            {"id": "1:2", "name": "ok"},
            {"id": "1:3", "name": "missing"},
        ]

        images_resp = MagicMock(status_code=200)
        images_resp.json.return_value = {"images": {"1:2": "https://cdn.figma.com/ok.png"}}

        img_resp = MagicMock(status_code=200, content=b"png")
        img_resp.raise_for_status = MagicMock()

        def mock_get(url, **kwargs):
            if "images" in url and "cdn" not in url:
                return images_resp
            return img_resp

        with patch("figma_to_code.requests.get", side_effect=mock_get), patch("sys.stderr"):
            result = export_frame_images("t", "k", frames)

        assert len(result) == 1
        assert result[0]["name"] == "ok"

    def test_empty_frames_returns_empty(self):
        from figma_to_code import export_frame_images

        with patch("figma_to_code.requests.get"):
            result = export_frame_images("t", "k", [])

        assert result == []

    def test_api_403_raises(self):
        from figma_to_code import export_frame_images, FigmaAPIError

        with patch("figma_to_code.requests.get") as mock:
            mock.return_value = MagicMock(status_code=403)
            with pytest.raises(FigmaAPIError, match="TOKEN"):
                export_frame_images("bad", "k", [{"id": "1", "name": "x"}])


class TestGenerateComponentCode:
    """OpenUI SSE 스트리밍 파싱 + JSX 코드 추출"""

    def _make_sse_lines(self, chunks):
        """OpenAI 호환 SSE 응답 라인 생성"""
        lines = []
        for chunk in chunks:
            import json
            lines.append(f"data: {json.dumps(chunk)}")
        lines.append("data: [DONE]")
        return "\n".join(lines)

    def _mock_response(self, sse_text):
        """requests.post mock 응답 생성"""
        lines = sse_text.split("\n")
        mock_resp = MagicMock(status_code=200)
        mock_resp.raise_for_status = MagicMock()
        mock_resp.iter_lines = MagicMock(
            return_value=iter(lines), decode_unicode=True
        )
        return mock_resp

    def test_returns_code_from_sse(self):
        from figma_to_code import generate_component_code

        chunks = [
            {"choices": [{"delta": {"content": "Here is ```jsx\n<div>"}}]},
            {"choices": [{"delta": {"content": "Hello</div>\n```"}}]},
        ]
        mock_resp = self._mock_response(self._make_sse_lines(chunks))

        with patch("figma_to_code.requests.post", return_value=mock_resp):
            result = generate_component_code("http://localhost:7878", "glm-5.1", "b64", "test-frame")

        assert result == "<div>Hello</div>"

    def test_no_code_block_returns_none(self):
        from figma_to_code import generate_component_code

        chunks = [
            {"choices": [{"delta": {"content": "Sorry, I cannot generate code."}}]},
        ]
        mock_resp = self._mock_response(self._make_sse_lines(chunks))

        with patch("figma_to_code.requests.post", return_value=mock_resp):
            result = generate_component_code("http://localhost:7878", "glm-5.1", "b64", "test")

        assert result is None

    def test_connection_error_returns_none(self):
        from figma_to_code import generate_component_code

        with patch("figma_to_code.requests.post", side_effect=Exception("Connection refused")), patch("sys.stderr"):
            result = generate_component_code("http://localhost:7878", "glm-5.1", "b64", "test")

        assert result is None

    def test_extracts_tsx_code_block(self):
        from figma_to_code import generate_component_code

        chunks = [
            {"choices": [{"delta": {"content": "```tsx\nexport default function App() { return <View />; }\n```"}}]},
        ]
        mock_resp = self._mock_response(self._make_sse_lines(chunks))

        with patch("figma_to_code.requests.post", return_value=mock_resp):
            result = generate_component_code("http://localhost:7878", "glm-5.1", "b64", "test")

        assert "export default function App()" in result


def test_to_pascal_case_kebab():
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
