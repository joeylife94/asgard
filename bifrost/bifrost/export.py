"""데이터 export"""

import csv
import json
from typing import List, Dict, Any
from io import StringIO
from datetime import datetime


class DataExporter:
    """데이터 export 유틸리티"""
    
    @staticmethod
    def to_csv(results: List[Dict[str, Any]]) -> str:
        """분석 결과를 CSV로 변환"""
        if not results:
            return ""
        
        output = StringIO()
        
        # 필드 정의
        fieldnames = [
            'id',
            'created_at',
            'source',
            'model',
            'service_name',
            'environment',
            'log_preview',
            'response_preview',
            'duration',
            'tokens_used',
            'cached',
            'tags',
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {
                'id': result.get('id', ''),
                'created_at': result.get('created_at', ''),
                'source': result.get('source', ''),
                'model': result.get('model', ''),
                'service_name': result.get('service_name', ''),
                'environment': result.get('environment', ''),
                'log_preview': DataExporter._truncate(result.get('log_content', ''), 100),
                'response_preview': DataExporter._truncate(result.get('response', ''), 200),
                'duration': result.get('duration', ''),
                'tokens_used': result.get('tokens_used', ''),
                'cached': result.get('cached', False),
                'tags': ','.join(result.get('tags', [])),
            }
            writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def to_json(results: List[Dict[str, Any]], pretty: bool = True) -> str:
        """JSON으로 변환"""
        if pretty:
            return json.dumps(results, indent=2, ensure_ascii=False, default=str)
        return json.dumps(results, ensure_ascii=False, default=str)
    
    @staticmethod
    def to_markdown_table(results: List[Dict[str, Any]]) -> str:
        """Markdown 테이블로 변환"""
        if not results:
            return "No results"
        
        lines = [
            "| ID | Created | Source | Service | Preview |",
            "|-----|---------|--------|---------|---------|"
        ]
        
        for result in results:
            lines.append(
                f"| {result.get('id', 'N/A')} "
                f"| {DataExporter._format_datetime(result.get('created_at'))} "
                f"| {result.get('source', 'N/A')} "
                f"| {result.get('service_name', 'N/A')} "
                f"| {DataExporter._truncate(result.get('response', ''), 50)} |"
            )
        
        return '\n'.join(lines)
    
    @staticmethod
    def to_html_table(results: List[Dict[str, Any]]) -> str:
        """HTML 테이블로 변환"""
        if not results:
            return "<p>No results</p>"
        
        html = ['<table class="table">']
        html.append('<thead><tr>')
        html.append('<th>ID</th><th>Created</th><th>Source</th><th>Service</th><th>Preview</th>')
        html.append('</tr></thead>')
        html.append('<tbody>')
        
        for result in results:
            html.append('<tr>')
            html.append(f'<td>{result.get("id", "N/A")}</td>')
            html.append(f'<td>{DataExporter._format_datetime(result.get("created_at"))}</td>')
            html.append(f'<td>{result.get("source", "N/A")}</td>')
            html.append(f'<td>{result.get("service_name", "N/A")}</td>')
            html.append(f'<td>{DataExporter._truncate(result.get("response", ""), 80)}</td>')
            html.append('</tr>')
        
        html.append('</tbody></table>')
        
        return '\n'.join(html)
    
    @staticmethod
    def _truncate(text: str, max_length: int) -> str:
        """텍스트 자르기"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def _format_datetime(dt: Any) -> str:
        """날짜 포맷"""
        if isinstance(dt, datetime):
            return dt.strftime('%Y-%m-%d %H:%M')
        elif isinstance(dt, str):
            return dt[:16]  # YYYY-MM-DD HH:MM
        return str(dt)
