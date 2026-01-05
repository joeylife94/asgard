"""커스텀 프롬프트 에디터 - 프롬프트 템플릿 생성, 수정, 버전 관리"""

from typing import Optional, List, Dict
from datetime import datetime
import json
from pathlib import Path

from bifrost.database import Database, get_database


class PromptEditor:
    """프롬프트 템플릿 에디터"""
    
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_database()
    
    def create_prompt(
        self,
        name: str,
        content: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        variables: Optional[List[str]] = None,
    ) -> int:
        """
        새 프롬프트 템플릿 생성
        
        Args:
            name: 프롬프트 이름 (고유)
            content: 프롬프트 내용 (변수는 {variable_name} 형식)
            description: 설명
            tags: 태그 리스트
            variables: 필요한 변수 리스트
        
        Returns:
            생성된 프롬프트 ID
        
        Examples:
            >>> editor = PromptEditor()
            >>> prompt_id = editor.create_prompt(
            ...     name="error_analysis",
            ...     content="다음 에러 로그를 분석하세요: {log_content}",
            ...     description="에러 로그 전문 분석",
            ...     tags=["error", "production"],
            ...     variables=["log_content"]
            ... )
        """
        # DB에 저장
        prompt_id = self.db.create_prompt_template(
            name=name,
            content=content,
            description=description,
            tags=tags or [],
        )
        
        # 변수 메타데이터 저장 (별도 테이블이나 JSON으로)
        if variables:
            self._save_variables_metadata(prompt_id, variables)
        
        return prompt_id
    
    def update_prompt(
        self,
        prompt_id: int,
        content: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """
        프롬프트 템플릿 업데이트 (버전 관리)
        
        Args:
            prompt_id: 업데이트할 프롬프트 ID
            content: 새 내용
            description: 새 설명
            tags: 새 태그
        
        Returns:
            업데이트 성공 여부
        """
        # 기존 프롬프트 조회
        old_prompt = self.db.get_prompt_template(prompt_id)
        if not old_prompt:
            return False
        
        # 버전 히스토리 저장
        self._save_version_history(prompt_id, old_prompt)
        
        # 업데이트
        return self.db.update_prompt_template(
            prompt_id=prompt_id,
            content=content,
            description=description,
            tags=tags,
        )
    
    def delete_prompt(self, prompt_id: int) -> bool:
        """
        프롬프트 템플릿 삭제 (soft delete)
        
        Args:
            prompt_id: 삭제할 프롬프트 ID
        
        Returns:
            삭제 성공 여부
        """
        return self.db.delete_prompt_template(prompt_id)
    
    def get_prompt(self, prompt_id: int) -> Optional[Dict]:
        """
        프롬프트 템플릿 조회
        
        Args:
            prompt_id: 조회할 프롬프트 ID
        
        Returns:
            프롬프트 정보 딕셔너리
        """
        return self.db.get_prompt_template(prompt_id)
    
    def list_prompts(
        self,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        프롬프트 템플릿 리스트 조회
        
        Args:
            tags: 필터링할 태그
            search: 검색 키워드 (name, description)
            limit: 최대 반환 개수
        
        Returns:
            프롬프트 리스트
        """
        return self.db.list_prompt_templates(
            tags=tags,
            search=search,
            limit=limit,
        )
    
    def render_prompt(
        self,
        prompt_id: int,
        variables: Dict[str, str],
    ) -> str:
        """
        프롬프트 렌더링 (변수 치환)
        
        Args:
            prompt_id: 렌더링할 프롬프트 ID
            variables: 치환할 변수 딕셔너리
        
        Returns:
            렌더링된 프롬프트 문자열
        
        Examples:
            >>> editor = PromptEditor()
            >>> rendered = editor.render_prompt(
            ...     prompt_id=1,
            ...     variables={"log_content": "ERROR: Failed to connect"}
            ... )
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        content = prompt["content"]
        
        # 변수 치환
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", value)
        
        return content
    
    def validate_prompt(self, content: str) -> Dict[str, any]:
        """
        프롬프트 유효성 검증
        
        Args:
            content: 검증할 프롬프트 내용
        
        Returns:
            검증 결과 딕셔너리
            - is_valid: bool
            - variables: List[str] - 발견된 변수들
            - errors: List[str] - 에러 메시지들
        """
        errors = []
        variables = []
        
        # 변수 추출 (정규식 사용)
        import re
        variable_pattern = r'\{(\w+)\}'
        found_vars = re.findall(variable_pattern, content)
        variables = list(set(found_vars))  # 중복 제거
        
        # 검증 규칙
        if len(content) < 10:
            errors.append("프롬프트가 너무 짧습니다 (최소 10자)")
        
        if len(content) > 10000:
            errors.append("프롬프트가 너무 깁니다 (최대 10000자)")
        
        # 중괄호 매칭 검증
        if content.count('{') != content.count('}'):
            errors.append("중괄호가 올바르게 닫히지 않았습니다")
        
        return {
            "is_valid": len(errors) == 0,
            "variables": variables,
            "errors": errors,
        }
    
    def get_version_history(self, prompt_id: int) -> List[Dict]:
        """
        프롬프트 버전 히스토리 조회
        
        Args:
            prompt_id: 조회할 프롬프트 ID
        
        Returns:
            버전 히스토리 리스트
        """
        history_file = self._get_history_file_path(prompt_id)
        if not history_file.exists():
            return []
        
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def rollback_version(self, prompt_id: int, version: int) -> bool:
        """
        특정 버전으로 롤백
        
        Args:
            prompt_id: 롤백할 프롬프트 ID
            version: 롤백할 버전 번호
        
        Returns:
            롤백 성공 여부
        """
        history = self.get_version_history(prompt_id)
        
        if version >= len(history):
            return False
        
        old_version = history[version]
        
        return self.db.update_prompt_template(
            prompt_id=prompt_id,
            content=old_version["content"],
            description=old_version.get("description"),
            tags=old_version.get("tags"),
        )
    
    def export_prompt(self, prompt_id: int, format: str = "json") -> str:
        """
        프롬프트를 파일로 export
        
        Args:
            prompt_id: export할 프롬프트 ID
            format: 포맷 (json, yaml, txt)
        
        Returns:
            export된 문자열
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        if format == "json":
            return json.dumps(prompt, indent=2, ensure_ascii=False)
        
        elif format == "yaml":
            import yaml
            return yaml.dump(prompt, allow_unicode=True)
        
        elif format == "txt":
            return f"""# {prompt['name']}
Description: {prompt.get('description', 'N/A')}
Tags: {', '.join(prompt.get('tags', []))}
Created: {prompt.get('created_at', 'N/A')}

---

{prompt['content']}
"""
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_prompt(self, file_path: str, format: str = "json") -> int:
        """
        파일에서 프롬프트 import
        
        Args:
            file_path: import할 파일 경로
            format: 파일 포맷 (json, yaml)
        
        Returns:
            생성된 프롬프트 ID
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            if format == "json":
                data = json.load(f)
            elif format == "yaml":
                import yaml
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        return self.create_prompt(
            name=data["name"],
            content=data["content"],
            description=data.get("description"),
            tags=data.get("tags", []),
        )
    
    # Private methods
    
    def _save_variables_metadata(self, prompt_id: int, variables: List[str]):
        """변수 메타데이터 저장"""
        metadata_dir = Path(".prompt_metadata")
        metadata_dir.mkdir(exist_ok=True)
        
        metadata_file = metadata_dir / f"prompt_{prompt_id}_vars.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "prompt_id": prompt_id,
                "variables": variables,
                "updated_at": datetime.now(datetime.UTC).isoformat(),
            }, f, indent=2)
    
    def _save_version_history(self, prompt_id: int, prompt_data: Dict):
        """버전 히스토리 저장"""
        history_dir = Path(".prompt_history")
        history_dir.mkdir(exist_ok=True)
        
        history_file = self._get_history_file_path(prompt_id)
        
        # 기존 히스토리 로드
        history = []
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # 새 버전 추가
        history.append({
            "version": len(history),
            "content": prompt_data.get("content"),
            "description": prompt_data.get("description"),
            "tags": prompt_data.get("tags", []),
            "updated_at": datetime.now(datetime.UTC).isoformat(),
        })
        
        # 저장
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def _get_history_file_path(self, prompt_id: int) -> Path:
        """히스토리 파일 경로 반환"""
        return Path(".prompt_history") / f"prompt_{prompt_id}_history.json"


# 편의 함수들

def create_default_prompts(db: Optional[Database] = None):
    """기본 프롬프트 템플릿 생성"""
    editor = PromptEditor(db)
    
    prompts = [
        {
            "name": "error_analysis",
            "content": """당신은 전문 SRE입니다. 다음 에러 로그를 분석하세요:

{log_content}

## 분석 항목:
1. 에러 유형 & 심각도
2. 발생 원인 (Root Cause)
3. 영향 범위
4. 해결 방법
5. 재발 방지책
""",
            "description": "에러 로그 전문 분석",
            "tags": ["error", "production", "sre"],
        },
        {
            "name": "performance_analysis",
            "content": """다음 성능 로그를 분석하여 병목 지점을 찾으세요:

{log_content}

## 분석 항목:
1. 느린 쿼리/API 호출
2. 리소스 사용량 (CPU, 메모리)
3. 병목 지점 (Bottleneck)
4. 최적화 제안
""",
            "description": "성능 로그 분석 및 최적화 제안",
            "tags": ["performance", "optimization"],
        },
        {
            "name": "security_audit",
            "content": """다음 로그에서 보안 이슈를 찾으세요:

{log_content}

## 점검 항목:
1. 비정상적인 접근 시도
2. 권한 상승 시도
3. 데이터 유출 가능성
4. 취약점 악용 시도
5. 보안 권장사항
""",
            "description": "보안 감사 로그 분석",
            "tags": ["security", "audit"],
        },
        {
            "name": "deployment_summary",
            "content": """다음 배포 로그를 요약하세요:

{log_content}

## 요약 항목:
1. 배포 성공 여부
2. 배포된 서비스/버전
3. 발생한 이슈
4. 롤백 필요 여부
5. 다음 배포 시 주의사항
""",
            "description": "배포 로그 요약",
            "tags": ["deployment", "ci-cd"],
        },
    ]
    
    created_ids = []
    for prompt in prompts:
        try:
            prompt_id = editor.create_prompt(**prompt)
            created_ids.append(prompt_id)
            print(f"✅ Created prompt: {prompt['name']} (ID: {prompt_id})")
        except Exception as e:
            print(f"❌ Failed to create {prompt['name']}: {e}")
    
    return created_ids


if __name__ == "__main__":
    # 데모
    editor = PromptEditor()
    
    # 기본 프롬프트 생성
    create_default_prompts()
    
    # 커스텀 프롬프트 생성
    custom_id = editor.create_prompt(
        name="my_custom_analysis",
        content="서비스: {service_name}\n로그: {log_content}\n분석해주세요.",
        description="나만의 커스텀 분석",
        tags=["custom"],
        variables=["service_name", "log_content"],
    )
    
    print(f"\n✅ Custom prompt created: ID {custom_id}")
    
    # 프롬프트 리스트
    prompts = editor.list_prompts()
    print(f"\n📋 Total prompts: {len(prompts)}")
    for p in prompts:
        print(f"  - {p['name']}: {p.get('description', 'N/A')}")
