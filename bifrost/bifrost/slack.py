"""Slack 통합"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class SlackNotifier:
    """Slack Webhook 알림"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
    
    def send_analysis_result(
        self, 
        result: Dict[str, Any],
        service_name: Optional[str] = None
    ) -> bool:
        """분석 결과를 Slack으로 전송"""
        if not self.webhook_url:
            return False
        
        try:
            # Slack 메시지 포맷
            blocks = self._format_message(result, service_name)
            
            response = requests.post(
                self.webhook_url,
                json={"blocks": blocks},
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            print(f"Slack 전송 실패: {e}")
            return False
    
    def _format_message(
        self, 
        result: Dict[str, Any],
        service_name: Optional[str]
    ) -> list:
        """Slack Block Kit 포맷"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🌈 Bifrost 로그 분석 결과",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*서비스:*\n{service_name or 'N/A'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*소스:*\n{result.get('source', 'local')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*시간:*\n{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*분석 ID:*\n{result.get('analysis_id', 'N/A')}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*분석 결과:*\n```{result.get('response', 'No response')[:3000]}```"
                }
            }
        ]
        
        # 태그가 있으면 추가
        if result.get('tags'):
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Tags: {', '.join(result['tags'])}"
                    }
                ]
            })
        
        return blocks
    
    def send_error_alert(
        self,
        error_message: str,
        service_name: Optional[str] = None
    ) -> bool:
        """에러 알림"""
        if not self.webhook_url:
            return False
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Bifrost 에러 알림",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*서비스:* {service_name or 'N/A'}\n*시간:* {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n```{error_message}```"
                    }
                }
            ]
            
            response = requests.post(
                self.webhook_url,
                json={"blocks": blocks},
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
