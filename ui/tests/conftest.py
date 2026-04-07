"""figma-to-code.py 모듈 import 설정.

파일명이 figma-to-code.py (하이픈)이므로 importlib으로 로드.
"""

import sys
import os
import importlib.util

scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
module_path = os.path.join(scripts_dir, "figma-to-code.py")

spec = importlib.util.spec_from_file_location("figma_to_code", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.modules["figma_to_code"] = module
