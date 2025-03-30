import os
import re


class TextCleaner:
    def __init__(self):
        self.stopwords = self._load_stopwords()

    def _load_stopwords(self) -> set:
        stopword_path = os.path.join(os.path.dirname(__file__), "stopwords_ko.txt")
        with open(stopword_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())

    def normalize_text(self, text: str) -> str:
        """
        텍스트를 소문자화하고 특수문자 제거 및 다중 공백 정리
        """
        text = text.lower()
        text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def remove_stopwords(self, text: str) -> str:
        """
        불용어 제거
        """
        tokens = text.split()
        filtered_tokens = [word for word in tokens if word not in self.stopwords]
        return " ".join(filtered_tokens)

    def clean(self, text: str) -> str:
        """
        전체 전처리 파이프라인 실행
        """
        normalized = self.normalize_text(text)
        cleaned = self.remove_stopwords(normalized)
        return cleaned