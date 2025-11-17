"""출력 포맷터 모듈"""

import json
from typing import Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax


class OutputFormatter:
    """출력 포맷터"""
    
    def __init__(self, format_type: str = "markdown", color: bool = True):
        self.format_type = format_type
        self.console = Console(color_system="auto" if color else None)
    
    def format(self, response: str, metadata: Dict[str, Any] = None):
        """응답 포맷팅 및 출력"""
        if self.format_type == "json":
            self._format_json(response, metadata)
        elif self.format_type == "plain":
            self._format_plain(response)
        else:  # markdown (default)
            self._format_markdown(response, metadata)
    
    def _format_markdown(self, response: str, metadata: Dict[str, Any] = None):
        """마크다운 포맷 출력"""
        self.console.print("\n" + "="*70)
        
        if metadata:
            info = f"🔮 모델: {metadata.get('model', 'N/A')} | " \
                   f"시간: {metadata.get('duration', 'N/A')}초"
            self.console.print(f"[dim]{info}[/dim]")
        
        md = Markdown(response)
        self.console.print(md)
        self.console.print("="*70 + "\n")
    
    def _format_json(self, response: str, metadata: Dict[str, Any] = None):
        """JSON 포맷 출력"""
        output = {
            "response": response,
            "metadata": metadata or {},
        }
        
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        self.console.print(syntax)
    
    def _format_plain(self, response: str):
        """플레인 텍스트 출력 (파이프 친화적)"""
        print(response)
    
    def print_error(self, message: str):
        """에러 메시지 출력"""
        if self.format_type == "plain":
            print(f"ERROR: {message}")
        else:
            self.console.print(f"[red]❌ {message}[/red]")
    
    def print_info(self, message: str):
        """정보 메시지 출력"""
        if self.format_type == "plain":
            print(f"INFO: {message}")
        else:
            self.console.print(f"[cyan]{message}[/cyan]")
    
    def print_warning(self, message: str):
        """경고 메시지 출력"""
        if self.format_type == "plain":
            print(f"WARNING: {message}")
        else:
            self.console.print(f"[yellow]⚠️  {message}[/yellow]")
    
    def print_stats(self, stats: Dict[str, Any]):
        """통계 정보 출력"""
        if self.format_type == "plain":
            for key, value in stats.items():
                print(f"{key}: {value}")
        else:
            panel = Panel.fit(
                "\n".join([f"[cyan]{k}:[/cyan] {v}" for k, v in stats.items()]),
                title="📊 로그 통계",
                border_style="blue",
            )
            self.console.print(panel)
