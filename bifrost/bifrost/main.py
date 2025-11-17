#!/usr/bin/env python3
"""Bifrost CLI - MLOps Log Analyzer"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from bifrost.ollama import OllamaClient
from bifrost.bedrock import BedrockClient, is_bedrock_available
from bifrost.config import Config
from bifrost.preprocessor import LogPreprocessor
from bifrost.formatter import OutputFormatter

app = typer.Typer(
    name="bifrost",
    help="🌈 The Rainbow Bridge for MLOps - AI-powered log analysis",
    add_completion=False,
)
console = Console()


MASTER_PROMPT = """당신은 전문 MLOps SRE입니다. 아래 로그를 분석하고 다음 형식으로 응답하세요:

## 📊 요약
로그의 핵심 내용을 3-5줄로 요약

## 🔍 주요 이슈
- 발견된 에러나 경고
- 중요한 패턴이나 이상 징후

## 💡 제안사항
- 문제 해결 방법
- 개선 방향

---
로그:
{log_content}
"""


@app.command()
def local(
    file_path: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="로그 파일 경로 (생략 시 stdin 사용)",
    ),
    ollama_url: Optional[str] = typer.Option(
        None,
        "--ollama-url",
        "-u",
        help="Ollama API URL",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="사용할 Ollama 모델",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="설정 파일 경로",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="출력 포맷 (markdown/json/plain)",
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="스트리밍 모드 활성화",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="상세 출력",
    ),
    no_preprocess: bool = typer.Option(
        False,
        "--no-preprocess",
        help="전처리 스킵",
    ),
):
    """
    🏠 로컬 모드 (Ollama) - 로그 분석
    
    예시:
    \b
    - bifrost local my-log.log
    - kubectl logs pod-name | bifrost local
    - cat error.log | bifrost local --stream
    - bifrost local app.log --format json
    """
    # 설정 로드
    config = Config(config_file)
    
    # CLI 옵션으로 오버라이드
    ollama_url = ollama_url or config.get("ollama.url")
    model = model or config.get("ollama.model")
    output_format = output_format or config.get("output.format")
    
    # 포맷터 초기화
    formatter = OutputFormatter(
        format_type=output_format,
        color=config.get("output.color", True),
    )
    
    # 입력 읽기
    formatter.print_info("🔮 로그 읽는 중...")
    log_content = _read_input(file_path)
    
    if not log_content.strip():
        formatter.print_error("입력된 로그가 비어있습니다.")
        raise typer.Exit(code=1)
    
    # 전처리
    if not no_preprocess:
        preprocessor = LogPreprocessor(
            max_size_mb=config.get("log.max_size_mb", 5),
            truncate=config.get("log.truncate", True),
            remove_timestamps=config.get("log.remove_timestamps", False),
        )
        
        original_stats = preprocessor.get_stats(log_content)
        log_content = preprocessor.process(log_content)
        processed_stats = preprocessor.get_stats(log_content)
        
        if verbose:
            formatter.print_stats({
                "원본 라인 수": original_stats["total_lines"],
                "처리 후 라인 수": processed_stats["total_lines"],
                "원본 크기": f"{original_stats['total_bytes'] / 1024:.1f} KB",
                "처리 후 크기": f"{processed_stats['total_bytes'] / 1024:.1f} KB",
            })
    
    # 프롬프트 생성
    prompt = MASTER_PROMPT.format(log_content=log_content)
    
    # Ollama 분석
    formatter.print_info(f"🔮 Ollama로 분석 중... (모델: {model})")
    
    try:
        client = OllamaClient(
            url=ollama_url,
            model=model,
            timeout=config.get("ollama.timeout", 120),
            max_retries=config.get("ollama.max_retries", 3),
        )
        
        result = client.analyze(prompt, stream=stream)
        
        # 결과 출력
        formatter.format(result["response"], result["metadata"])
        
    except Exception as e:
        formatter.print_error(f"분석 실패: {e}")
        raise typer.Exit(code=1)


@app.command()
def batch(
    directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="로그 파일 디렉토리",
    ),
    pattern: str = typer.Option(
        "*.log",
        "--pattern",
        "-p",
        help="파일 패턴 (glob)",
    ),
    source: str = typer.Option(
        "local",
        "--source",
        help="분석 소스 (local/cloud)",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="모델명",
    ),
    max_workers: int = typer.Option(
        4,
        "--workers",
        "-w",
        help="동시 실행 워커 수",
    ),
):
    """
    📦 배치 모드 - 디렉토리 내 로그 일괄 분석
    
    예시:
    \b
    - bifrost batch ./logs
    - bifrost batch ./logs --pattern "*.txt"
    - bifrost batch ./logs --workers 8
    """
    from bifrost.batch import BatchAnalyzer
    
    analyzer = BatchAnalyzer(
        source=source,
        model=model,
        max_workers=max_workers,
    )
    
    results = analyzer.analyze_directory(directory, pattern)
    
    # 결과 요약
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    cached = sum(1 for r in results if r.get("cached", False))
    failed = sum(1 for r in results if r["status"] == "failed")
    
    console.print(f"\n[green]✅ 완료: {success}/{total}[/green]")
    console.print(f"[blue]📦 캐시 히트: {cached}[/blue]")
    if failed > 0:
        console.print(f"[red]❌ 실패: {failed}[/red]")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", help="호스트"),
    port: int = typer.Option(8000, "--port", help="포트"),
    reload: bool = typer.Option(False, "--reload", help="자동 리로드"),
):
    """
    🌐 API 서버 시작
    
    예시:
    \b
    - bifrost serve
    - bifrost serve --port 9000 --reload
    """
    import uvicorn
    uvicorn.run(
        "bifrost.api:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def cloud(
    file_path: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="로그 파일 경로 (생략 시 stdin 사용)",
    ),
    region: Optional[str] = typer.Option(
        None,
        "--region",
        "-r",
        help="AWS 리전",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Bedrock 모델 ID",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="AWS 프로파일",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="설정 파일 경로",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="출력 포맷 (markdown/json/plain)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="상세 출력",
    ),
):
    """
    ☁️  클라우드 모드 (AWS Bedrock) - 로그 분석
    
    예시:
    \b
    - bifrost cloud my-log.log
    - kubectl logs pod-name | bifrost cloud
    - bifrost cloud app.log --region us-west-2
    """
    if not is_bedrock_available():
        console.print("[red]❌ boto3가 설치되지 않았습니다.[/red]")
        console.print("설치: pip install boto3")
        raise typer.Exit(code=1)
    
    # 설정 로드
    config = Config(config_file)
    
    # CLI 옵션으로 오버라이드
    region = region or config.get("bedrock.region")
    model = model or config.get("bedrock.model")
    profile = profile or config.get("bedrock.profile")
    output_format = output_format or config.get("output.format")
    
    # 포맷터 초기화
    formatter = OutputFormatter(
        format_type=output_format,
        color=config.get("output.color", True),
    )
    
    # 입력 읽기
    formatter.print_info("🔮 로그 읽는 중...")
    log_content = _read_input(file_path)
    
    if not log_content.strip():
        formatter.print_error("입력된 로그가 비어있습니다.")
        raise typer.Exit(code=1)
    
    # 전처리
    preprocessor = LogPreprocessor(
        max_size_mb=config.get("log.max_size_mb", 5),
        truncate=config.get("log.truncate", True),
    )
    log_content = preprocessor.process(log_content)
    
    if verbose:
        stats = preprocessor.get_stats(log_content)
        formatter.print_stats(stats)
    
    # 프롬프트 생성
    prompt = MASTER_PROMPT.format(log_content=log_content)
    
    # Bedrock 분석
    formatter.print_info(f"☁️  AWS Bedrock로 분석 중... (리전: {region})")
    
    try:
        client = BedrockClient(
            region=region,
            model_id=model,
            profile=profile,
        )
        
        result = client.analyze(prompt)
        
        # 결과 출력
        formatter.format(result["response"], result["metadata"])
        
    except Exception as e:
        formatter.print_error(f"분석 실패: {e}")
        raise typer.Exit(code=1)


@app.command()
def config(
    init: bool = typer.Option(
        False,
        "--init",
        help="샘플 설정 파일 생성",
    ),
    path: Path = typer.Option(
        Path.cwd() / "bifrost.yaml",
        "--path",
        "-p",
        help="설정 파일 경로",
    ),
    show: bool = typer.Option(
        False,
        "--show",
        help="현재 설정 표시",
    ),
):
    """
    ⚙️  설정 관리
    
    예시:
    \b
    - bifrost config --init
    - bifrost config --show
    """
    if init:
        if path.exists():
            console.print(f"[yellow]⚠️  파일이 이미 존재합니다: {path}[/yellow]")
            if not typer.confirm("덮어쓰시겠습니까?"):
                raise typer.Exit()
        
        Config.create_sample_config(path)
        console.print(f"[green]✅ 설정 파일 생성됨: {path}[/green]")
    
    elif show:
        config = Config()
        import yaml
        console.print("\n현재 설정:")
        console.print(yaml.dump(config.data, allow_unicode=True, default_flow_style=False))
    
    else:
        console.print("사용법: bifrost config --init 또는 --show")


def _read_input(file_path: Optional[Path]) -> str:
    """파일 또는 stdin에서 입력 읽기"""
    if file_path:
        # 파일에서 읽기
        return file_path.read_text(encoding="utf-8")
    else:
        # stdin 체크
        if sys.stdin.isatty():
            # stdin이 비어있음 (파이프 없음)
            console.print("[red]❌ 파일 경로를 제공하거나 stdin으로 데이터를 파이프하세요.[/red]")
            console.print("\n사용 예시:")
            console.print("  bifrost local my-log.log")
            console.print("  cat my-log.log | bifrost local")
            raise typer.Exit(code=1)
        else:
            # stdin에서 읽기
            return sys.stdin.read()


@app.command()
def filter_log(
    file: typer.FileText = typer.Argument(..., help="로그 파일"),
    severity: str = typer.Option("INFO", help="최소 심각도 (DEBUG/INFO/WARN/ERROR/FATAL)"),
    errors_only: bool = typer.Option(False, "--errors-only", help="에러만 추출"),
    output: Optional[typer.FileTextWrite] = typer.Option(None, help="출력 파일"),
):
    """로그 필터링
    
    예시:
    \b
    - bifrost filter-log app.log --severity ERROR
    - bifrost filter-log app.log --errors-only
    - bifrost filter-log app.log --severity WARN --output filtered.log
    """
    from bifrost.filters import LogFilter, SeverityLevel
    from datetime import datetime
    
    log_content = file.read()
    
    if errors_only:
        filtered = LogFilter.extract_errors_only(log_content)
    else:
        try:
            min_level = SeverityLevel(severity.upper())
            filtered = LogFilter.filter_by_severity(log_content, min_level)
        except ValueError:
            console.print(f"[red]Invalid severity level: {severity}[/red]")
            console.print("Valid values: TRACE, DEBUG, INFO, WARN, ERROR, FATAL")
            raise typer.Exit(1)
    
    # 통계 출력
    stats = LogFilter.get_log_statistics(filtered)
    console.print(f"\n📊 Filtered Log Statistics:", style="bold")
    console.print(f"Total lines: {stats['total_lines']}")
    console.print(f"By severity: {stats['by_severity']}")
    
    # 결과 출력
    if output:
        output.write(filtered)
        console.print(f"\n✅ Filtered log saved to: {output.name}", style="green")
    else:
        console.print(f"\n{filtered}")


@app.command()
def export(
    format: str = typer.Option("csv", help="Export 포맷 (csv/json)"),
    limit: int = typer.Option(100, help="Export할 레코드 수"),
    output: Optional[str] = typer.Option(None, help="출력 파일명"),
):
    """분석 결과 export
    
    예시:
    \b
    - bifrost export --format csv --limit 50
    - bifrost export --format json --output results.json
    """
    from bifrost.database import Database
    from bifrost.export import DataExporter
    from datetime import datetime
    
    config = Config()
    db = Database(config.get("database.url", "sqlite:///bifrost.db"))
    
    results = db.get_analysis_history(limit=limit)
    
    if not results:
        console.print("[yellow]No analysis results found[/yellow]")
        raise typer.Exit(0)
    
    # Export
    if format == "csv":
        content = DataExporter.to_csv(results)
        default_filename = f"bifrost_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    elif format == "json":
        content = DataExporter.to_json(results, pretty=True)
        default_filename = f"bifrost_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:
        console.print(f"[red]Invalid format: {format}[/red]")
        console.print("Valid formats: csv, json")
        raise typer.Exit(1)
    
    output_file = output or default_filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    console.print(f"✅ Exported {len(results)} results to: {output_file}", style="green")


@app.command()
def slack(
    webhook_url: str = typer.Option(..., help="Slack Webhook URL"),
    file: Optional[typer.FileText] = typer.Option(None, help="로그 파일"),
    message: Optional[str] = typer.Option(None, help="직접 메시지"),
    service_name: Optional[str] = typer.Option(None, help="서비스명"),
):
    """Slack으로 알림 전송
    
    예시:
    \b
    - bifrost slack --webhook-url https://hooks.slack.com/... --file app.log
    - bifrost slack --webhook-url https://hooks.slack.com/... --message "Deploy failed"
    """
    from bifrost.slack import SlackNotifier
    
    notifier = SlackNotifier(webhook_url)
    
    if file:
        # 로그 분석 후 전송
        log_content = file.read()
        
        preprocessor = LogPreprocessor()
        processed = preprocessor.process(log_content)
        
        client = OllamaClient()
        result = client.analyze(processed)
        
        success = notifier.send_analysis_result(result, service_name)
    
    elif message:
        # 에러 메시지 전송
        success = notifier.send_error_alert(message, service_name)
    
    else:
        console.print("[red]Either --file or --message is required[/red]")
        raise typer.Exit(1)
    
    if success:
        console.print("✅ Slack 전송 성공!", style="green")
    else:
        console.print("❌ Slack 전송 실패", style="red")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
