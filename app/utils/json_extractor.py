# SPDX-License-Identifier: Apache-2.0
import json
import re

def extract_json_from_response(response_str: str) -> dict:
    """
    LLM 응답 문자열에서 JSON만 추출하여 dict로 반환
    """
    try:
        json_match = re.search(r'{[\s\S]*?}', response_str)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("JSON 형식을 찾을 수 없습니다.")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}")
