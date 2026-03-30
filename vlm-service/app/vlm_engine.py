"""vLLM 기반 VLM 추론 엔진."""

import json
import re

from vllm import LLM, SamplingParams

from .config import settings
from .prompt import PROMPT_TEMPLATE, SYSTEM_PROMPT


class VLMEngine:
    def __init__(self):
        self.llm = LLM(
            model=settings.model_name,
            max_model_len=settings.max_model_len,
            gpu_memory_utilization=settings.gpu_memory_utilization,
            trust_remote_code=settings.trust_remote_code,
        )
        self.sampling_params = SamplingParams(temperature=0.1, max_tokens=2048)

    def analyze(self, image_bytes: bytes, yolo_class: str, confidence: float, region: str) -> dict:
        region_info = f"{region} 지역 기준" if region else "기본 지역 기준"
        prompt = PROMPT_TEMPLATE.format(yolo_class=yolo_class, confidence=confidence, region_info=region_info)

        inputs = {
            "prompt": SYSTEM_PROMPT + "\n\n" + prompt,
            "multi_modal_data": {"image": image_bytes},
        }

        outputs = self.llm.generate([inputs], self.sampling_params)
        response_text = outputs[0].outputs[0].text

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return self._parse_json_from_text(response_text)

    def _parse_json_from_text(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {
            "waste_type": "분류 불가",
            "disposal_method": {"method": "다시 시도해주세요", "notes": [], "items": []},
            "cost_info": "",
            "warnings": "분류 실패",
            "confidence": 0.0,
        }
