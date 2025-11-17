"""다국어 지원 (Internationalization) - 한국어/영어 메시지 번역"""

import json
from typing import Dict, Optional
from pathlib import Path
from enum import Enum


class Language(str, Enum):
    """지원 언어"""
    KOREAN = "ko"
    ENGLISH = "en"


class I18n:
    """국제화 (i18n) 클래스"""
    
    def __init__(self, default_language: Language = Language.KOREAN):
        """
        I18n 초기화
        
        Args:
            default_language: 기본 언어
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        
        # 번역 파일 로드
        self._load_translations()
    
    def _load_translations(self):
        """번역 파일 로드"""
        locales_dir = Path(__file__).parent.parent / "locales"
        
        for lang in Language:
            locale_file = locales_dir / f"{lang.value}.json"
            if locale_file.exists():
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations[lang.value] = json.load(f)
    
    def set_language(self, language: Language):
        """
        현재 언어 설정
        
        Args:
            language: 설정할 언어
        """
        self.current_language = language
    
    def t(
        self,
        key: str,
        lang: Optional[Language] = None,
        **kwargs
    ) -> str:
        """
        번역 (translate)
        
        Args:
            key: 번역 키 (예: "error.database_connection")
            lang: 언어 (None이면 current_language 사용)
            **kwargs: 포맷 변수들
        
        Returns:
            번역된 문자열
        
        Examples:
            >>> i18n = I18n()
            >>> i18n.t("greeting.hello", name="철수")
            "안녕하세요, 철수님!"
            
            >>> i18n.t("greeting.hello", lang=Language.ENGLISH, name="John")
            "Hello, John!"
        """
        lang = lang or self.current_language
        
        # 번역 찾기
        translation = self.translations.get(lang.value, {}).get(key)
        
        # 번역 없으면 기본 언어 시도
        if not translation and lang != self.default_language:
            translation = self.translations.get(
                self.default_language.value, {}
            ).get(key)
        
        # 그래도 없으면 키 자체 반환
        if not translation:
            return key
        
        # 변수 치환
        try:
            return translation.format(**kwargs)
        except KeyError:
            return translation
    
    def get_all_languages(self) -> list[Language]:
        """지원하는 모든 언어 반환"""
        return list(Language)
    
    def get_current_language(self) -> Language:
        """현재 언어 반환"""
        return self.current_language


# 전역 i18n 인스턴스
_i18n = I18n()


def t(key: str, **kwargs) -> str:
    """
    전역 번역 함수 (간편 사용)
    
    Examples:
        >>> from bifrost.i18n import t
        >>> print(t("error.not_found"))
    """
    return _i18n.t(key, **kwargs)


def set_language(language: Language):
    """전역 언어 설정"""
    _i18n.set_language(language)


def get_language() -> Language:
    """현재 언어 조회"""
    return _i18n.get_current_language()


if __name__ == "__main__":
    # 데모
    i18n = I18n()
    
    # 한국어 (기본)
    print(i18n.t("greeting.hello", name="철수"))
    print(i18n.t("analysis.start"))
    
    # 영어
    print(i18n.t("greeting.hello", lang=Language.ENGLISH, name="John"))
    print(i18n.t("analysis.start", lang=Language.ENGLISH))
    
    # 변수 치환
    print(i18n.t("analysis.complete", duration=2.5, count=10))
