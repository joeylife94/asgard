#!/usr/bin/env python
"""빠른 데모 스크립트"""

import requests
import json
from pathlib import Path

# API 베이스 URL
BASE_URL = "http://localhost:8000"

def demo_analyze():
    """로그 분석 데모"""
    print("🌈 Bifrost API 데모\n")
    
    # 샘플 로그
    log_content = """
2024-10-25 10:15:32 ERROR [main] Database connection failed
2024-10-25 10:15:33 ERROR [main] java.sql.SQLException: Connection refused
2024-10-25 10:15:34 WARN  [main] Retrying connection...
2024-10-25 10:15:39 ERROR [main] Max retries reached
"""
    
    # 분석 요청
    print("📤 분석 요청 중...")
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={
            "log_content": log_content,
            "source": "local",
            "service_name": "demo-app",
            "tags": ["demo", "error"],
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 분석 완료! (ID: {result['id']})")
        print(f"⏱️  소요 시간: {result['duration_seconds']}초")
        print(f"\n📊 분석 결과:\n{result['response']}\n")
    else:
        print(f"❌ 오류: {response.text}")


def demo_history():
    """히스토리 조회 데모"""
    print("📜 최근 분석 히스토리\n")
    
    response = requests.post(
        f"{BASE_URL}/history",
        json={"limit": 5}
    )
    
    if response.status_code == 200:
        results = response.json()
        for r in results:
            print(f"ID: {r['id']} | 모델: {r['model']} | 서비스: {r['service_name']}")
    else:
        print(f"❌ 오류: {response.text}")


def demo_metrics():
    """메트릭 조회 데모"""
    print("\n📈 시스템 메트릭\n")
    
    response = requests.get(f"{BASE_URL}/metrics?hours=24")
    
    if response.status_code == 200:
        metrics = response.json()
        print(f"총 분석 수: {metrics['total_analyses']}")
        print(f"평균 소요 시간: {metrics['avg_duration_seconds']}초")
        print(f"\n모델별 통계:")
        for stat in metrics['model_stats']:
            print(f"  - {stat['model']}: {stat['count']}건 (평균 {stat['avg_duration']}초)")
    else:
        print(f"❌ 오류: {response.text}")


if __name__ == "__main__":
    try:
        # 헬스 체크
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API 서버가 실행 중이 아닙니다.")
            print("   실행: bifrost serve")
            exit(1)
        
        # 데모 실행
        demo_analyze()
        demo_history()
        demo_metrics()
        
        print("\n✨ 데모 완료!")
    
    except requests.exceptions.ConnectionError:
        print("❌ API 서버에 연결할 수 없습니다.")
        print("   먼저 서버를 시작하세요: bifrost serve")
