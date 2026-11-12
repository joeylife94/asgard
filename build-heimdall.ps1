# Heimdall 빌드 스크립트
# VSCode 및 IntelliJ IDEA 모두 지원

Write-Host "🔧 Heimdall 빌드 가이드" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== 빌드 방법 ===" -ForegroundColor Yellow
Write-Host ""

Write-Host "방법 1: VSCode에서 빌드 (추천)" -ForegroundColor Green
Write-Host "1. VSCode에서 asgard 폴더 열기"
Write-Host "2. 터미널에서 실행 (Ctrl + `):"
Write-Host '   $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot"'
Write-Host '   $env:Path = "$env:JAVA_HOME\bin;" + $env:Path'
Write-Host "   .\gradlew.bat :heimdall:clean :heimdall:bootJar -x test -x checkstyleMain -x checkstyleTest"
Write-Host ""
Write-Host "3. 빌드 완료 후 JAR 파일 확인:"
Write-Host "   heimdall\build\libs\heimdall-1.0.0.jar"
Write-Host ""

Write-Host "방법 2: VSCode에서 테스트 실행" -ForegroundColor Green
Write-Host "1. 터미널에서 Unit Test 실행:"
Write-Host '   $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot"'
Write-Host '   $env:Path = "$env:JAVA_HOME\bin;" + $env:Path'
Write-Host "   .\gradlew.bat :heimdall:test --tests HealthControllerTest -x checkstyleMain -x checkstyleTest"
Write-Host ""
Write-Host "2. 테스트 결과 확인:"
Write-Host "   start heimdall\build\reports\tests\test\index.html"
Write-Host "   start heimdall\build\reports\jacoco\test\html\index.html"
Write-Host ""

Write-Host "방법 3: IntelliJ IDEA" -ForegroundColor Green
Write-Host "1. IntelliJ IDEA에서 asgard 폴더 열기 (File → Open)"
Write-Host "2. Gradle 동기화 대기 (자동으로 wrapper 복구됨)"
Write-Host "3. Gradle 창에서: heimdall → Tasks → build → bootJar 더블클릭"
Write-Host "4. 또는 터미널에서 실행:"
Write-Host "   cd heimdall"
Write-Host "   .\gradlew.bat clean bootJar -x test"
Write-Host ""

Write-Host "방법 4: IntelliJ에서 직접 실행 (테스트용)" -ForegroundColor Green
Write-Host "1. src/main/java/com/heimdall/HeimdallApplication.java 열기"
Write-Host "2. Run 'HeimdallApplication' 클릭"
Write-Host "3. VM Options에 추가: -Dspring.profiles.active=local"
Write-Host "4. http://localhost:8080/api/v1/health 확인"
Write-Host ""

Write-Host "방법 5: Gradle 직접 설치 (선택사항)" -ForegroundColor Green
Write-Host "1. winget install Gradle.Gradle"
Write-Host "2. cd heimdall"
Write-Host "3. gradle wrapper --gradle-version 8.5"
Write-Host "4. .\gradlew.bat clean bootJar -x test"
Write-Host ""

Write-Host "=== 실행 방법 ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "JAR 빌드 후:" -ForegroundColor Cyan
Write-Host '  $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot"'
Write-Host '  $env:Path = "$env:JAVA_HOME\bin;" + $env:Path'
Write-Host "  java -jar heimdall\build\libs\heimdall-0.1.0.jar --spring.profiles.active=local"
Write-Host ""

Write-Host "=== API 테스트 ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Heimdall 실행 후:" -ForegroundColor Cyan
Write-Host "  .\test-api.ps1"
Write-Host ""

Write-Host "=== K6 스트레스 테스트 ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. K6 설치:" -ForegroundColor Cyan
Write-Host "   winget install k6 --source winget"
Write-Host ""
Write-Host "2. 테스트 실행:"
Write-Host "   k6 run heimdall\src\test\k6\stress-test.js"
Write-Host ""

Write-Host "=== 모니터링 대시보드 ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "Grafana:    http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "Zipkin:     http://localhost:9411" -ForegroundColor Cyan
Write-Host "Kafka UI:   http://localhost:8090" -ForegroundColor Cyan
Write-Host ""

Write-Host "✨ 준비 완료! VSCode 또는 IntelliJ IDEA로 프로젝트를 시작하세요." -ForegroundColor Green
Write-Host ""
Write-Host "💡 VSCode 사용자: 위의 방법 1, 2를 따라 빌드 및 테스트를 진행하세요!" -ForegroundColor Yellow
Write-Host "💡 IntelliJ 사용자: 위의 방법 3, 4를 따라 프로젝트를 열고 실행하세요!" -ForegroundColor Yellow
