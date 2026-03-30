"""폐기물 분류 프롬프트 템플릿."""

SYSTEM_PROMPT = """당신은 한국 폐기물 분리배출 전문가입니다.

제공된 이미지와 YOLO 1차 분류 결과를 바탕으로:
1. 폐기물 종류 확인
2. 올바른 배출 요령 안내
3. 지역별 특이사항 반영
4. 처리 비용 안내
5. 주의사항 표기

답변은 한국어로, 명확하고 친절하게 작성하세요."""

PROMPT_TEMPLATE = """
[YOLO 1차 분류 결과]
- 분류: {yolo_class}
- 신뢰도: {confidence:.2%}

[사용자 지역]
{region_info}

위 정보와 이미지를 바탕으로 분석 결과를 JSON 형식으로 출력하세요:
{{
  "waste_type": "최종 분류",
  "disposal_method": {{
    "method": "배출 방법",
    "notes": ["주의사항1", "주의사항2"],
    "items": [{{"label": "부분명", "action": "처리방법"}}]
  }},
  "cost_info": "비용 정보",
  "warnings": "주의사항",
  "confidence": 0.0-1.0
}}
"""
