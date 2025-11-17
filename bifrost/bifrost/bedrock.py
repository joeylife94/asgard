"""AWS Bedrock API 통신 모듈 (v0.2 준비)"""

import json
import time
from typing import Dict, Any, Optional

# boto3는 선택적 의존성
try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False


class BedrockClient:
    """AWS Bedrock 클라이언트"""
    
    def __init__(
        self,
        region: str = "us-east-1",
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        profile: Optional[str] = None,
    ):
        if not BEDROCK_AVAILABLE:
            raise ImportError(
                "boto3가 설치되지 않았습니다.\n"
                "설치: pip install boto3"
            )
        
        self.region = region
        self.model_id = model_id
        self.profile = profile
        
        # Bedrock Runtime 클라이언트 생성
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client(
            service_name="bedrock-runtime",
            region_name=region,
        )
    
    def analyze(self, prompt: str) -> Dict[str, Any]:
        """
        로그 분석 (Claude 3 API 사용)
        
        Returns:
            {"response": str, "metadata": dict}
        """
        try:
            start_time = time.time()
            
            # Claude 3 메시지 포맷
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.7,
            })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            
            duration = time.time() - start_time
            
            # 응답 파싱
            response_body = json.loads(response['body'].read())
            
            # Claude 3 응답 구조
            content = response_body.get('content', [])
            if content and isinstance(content, list):
                response_text = content[0].get('text', '')
            else:
                response_text = str(content)
            
            return {
                "response": response_text,
                "metadata": {
                    "model": self.model_id,
                    "duration": round(duration, 2),
                    "region": self.region,
                    "usage": response_body.get('usage', {}),
                }
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                raise Exception(
                    f"AWS Bedrock 액세스 거부: {error_msg}\n"
                    "IAM 권한을 확인하세요 (bedrock:InvokeModel 필요)"
                )
            elif error_code == 'ThrottlingException':
                raise Exception(f"요청 제한 초과: {error_msg}")
            else:
                raise Exception(f"Bedrock API 오류 [{error_code}]: {error_msg}")
        
        except BotoCoreError as e:
            raise Exception(f"AWS SDK 오류: {e}")
        
        except Exception as e:
            raise Exception(f"Bedrock 요청 실패: {e}")
    
    def health_check(self) -> bool:
        """Bedrock 사용 가능 여부 확인"""
        try:
            # 모델 리스트 조회로 간단히 체크
            self.client.list_foundation_models(maxResults=1)
            return True
        except:
            return False


def is_bedrock_available() -> bool:
    """Bedrock 사용 가능 여부 (boto3 설치 확인)"""
    return BEDROCK_AVAILABLE
