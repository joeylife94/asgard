FROM gradle:8-jdk17 AS builder

WORKDIR /workspace

# Copy root Gradle project files (multi-module build)
COPY gradlew gradlew.bat settings.gradle build.gradle gradle.properties ./
COPY gradle ./gradle
COPY config ./config

RUN sed -i 's/\r$//' gradlew && chmod +x gradlew

# Copy Heimdall module sources
COPY heimdall ./heimdall

# Build Heimdall only (skip tests for container build)
RUN ./gradlew :heimdall:bootJar -x test --no-daemon

FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Add non-root user
RUN addgroup -g 1000 heimdall && \
    adduser -D -u 1000 -G heimdall heimdall

RUN mkdir -p /app/logs

# Copy JAR from builder
COPY --from=builder /workspace/heimdall/build/libs/*.jar app.jar

# Change ownership
RUN chown -R heimdall:heimdall /app

USER heimdall

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
