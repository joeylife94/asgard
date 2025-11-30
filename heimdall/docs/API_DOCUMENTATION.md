# API Documentation (Swagger/OpenAPI)

This document describes the API documentation setup for Heimdall using SpringDoc OpenAPI.

## Overview

Heimdall uses **SpringDoc OpenAPI 3** to automatically generate interactive API documentation with Swagger UI.

## Access

### Local Development

- **Swagger UI:** http://localhost:8080/swagger-ui.html
- **OpenAPI JSON:** http://localhost:8080/v3/api-docs
- **OpenAPI YAML:** http://localhost:8080/v3/api-docs.yaml

### Production

- **Swagger UI:** https://api.asgard.example.com/swagger-ui.html
- **OpenAPI JSON:** https://api.asgard.example.com/v3/api-docs

## Configuration

### Dependencies

```gradle
// SpringDoc OpenAPI (Swagger)
implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.3.0'
```

### Application Configuration

Located in `application.yml`:

```yaml
springdoc:
  api-docs:
    enabled: true
    path: /v3/api-docs
  swagger-ui:
    enabled: true
    path: /swagger-ui.html
    operationsSorter: method
    tagsSorter: alpha
    display-request-duration: true
    filter: true
  show-actuator: false
```

### Security Configuration

Swagger UI is publicly accessible (no authentication required):

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
    // ...
)
```

## Using Swagger UI

### 1. Access Swagger UI

Open your browser and navigate to:
```
http://localhost:8080/swagger-ui.html
```

### 2. Authenticate

To test protected endpoints:

1. Click **"Authorize"** button (lock icon) at the top right
2. Login to get JWT token:
   - **URL:** POST `/api/auth/login`
   - **Body:**
     ```json
     {
       "username": "developer",
       "password": "dev123"
     }
     ```
3. Copy the `accessToken` from response
4. Paste the token (without "Bearer " prefix)
5. Click **"Authorize"**

### 3. Test Endpoints

#### Health Check (No Auth Required)

```
GET /api/bifrost/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "bifrost"
}
```

#### Analyze Log (Auth Required)

```
POST /api/bifrost/analyze
```

**Request Body:**
```json
{
  "log": "NullPointerException at line 42",
  "level": "ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 3600
```

**Response Body:**
```json
{
  "analysis": "Memory access violation detected",
  "severity": "HIGH",
  "recommendations": [
    "Check null pointer handling"
  ]
}
```

### 4. Monitor Rate Limits

All API responses include rate limit headers:

- **X-RateLimit-Limit:** Maximum requests allowed
- **X-RateLimit-Remaining:** Remaining requests in current window
- **X-RateLimit-Reset:** Seconds until limit resets

When rate limit is exceeded:

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later.",
  "retryAfter": 1234
}
```

## API Groups

### Authentication (`/api/auth`)

No authentication required:

- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info (requires auth)
- `GET /api/auth/validate` - Validate JWT token
- `POST /api/auth/logout` - Logout

### Bifrost Integration (`/api/bifrost`)

Requires authentication (ROLE_DEVELOPER or ROLE_ADMIN):

- `GET /api/bifrost/health` - Check Bifrost service health
- `POST /api/bifrost/analyze` - Analyze log entry (sync)
- `POST /api/bifrost/analyze/async` - Analyze log entry (async)
- `GET /api/bifrost/history` - Get analysis history

### Actuator (`/actuator`)

Public endpoints:

- `GET /actuator/health` - Application health check
- `GET /actuator/info` - Application info

Protected endpoints (requires ROLE_ADMIN):

- `GET /actuator/metrics` - Metrics
- `GET /actuator/prometheus` - Prometheus metrics
- `GET /actuator/circuitbreakers` - Circuit breaker status
- `GET /actuator/circuitbreakerevents` - Circuit breaker events

## OpenAPI Configuration

### API Information

```java
@Configuration
public class OpenApiConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Heimdall API Gateway")
                        .version("1.0.0")
                        .description("MSA 로그 분석 플랫폼 API Gateway")
                        .contact(new Contact()
                                .name("Asgard Team")
                                .email("support@asgard.example.com")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8080")
                                .description("Development Server")))
                .components(new Components()
                        .addSecuritySchemes("bearer-jwt", 
                                new SecurityScheme()
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")));
    }
}
```

### Controller Annotations

```java
@RestController
@RequestMapping("/api/bifrost")
@Tag(name = "Bifrost Integration", description = "ML/AI log analysis")
@SecurityRequirement(name = "bearer-jwt")
public class BifrostController {
    
    @Operation(
        summary = "Analyze log entry",
        description = "Send log data to Bifrost for ML/AI analysis"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Analysis completed successfully"
        ),
        @ApiResponse(
            responseCode = "429",
            description = "Rate limit exceeded"
        )
    })
    @PostMapping("/analyze")
    @RateLimit(maxRequests = 100, duration = 1, timeUnit = ChronoUnit.HOURS)
    public ResponseEntity<Map<String, Object>> analyzeLog(
            @RequestBody Map<String, Object> logData) {
        // ...
    }
}
```

## Customization

### Change Swagger UI Path

```yaml
springdoc:
  swagger-ui:
    path: /api-docs  # Default: /swagger-ui.html
```

### Disable in Production

```yaml
spring:
  profiles:
    active: prod

---
spring:
  config:
    activate:
      on-profile: prod

springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
```

### Custom OpenAPI YAML

```yaml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    url: /custom-api-spec.yaml
```

## Best Practices

### 1. Document All Endpoints

Use `@Operation`, `@ApiResponse`, `@Parameter` annotations:

```java
@Operation(summary = "Get user by ID")
@ApiResponses(value = {
    @ApiResponse(responseCode = "200", description = "User found"),
    @ApiResponse(responseCode = "404", description = "User not found")
})
@GetMapping("/{id}")
public ResponseEntity<User> getUser(
        @Parameter(description = "User ID") @PathVariable Long id) {
    // ...
}
```

### 2. Group Related Endpoints

```java
@Tag(name = "User Management", description = "User CRUD operations")
@RestController
@RequestMapping("/api/users")
public class UserController { ... }
```

### 3. Include Examples

```java
@Schema(example = "user@example.com")
private String email;

@Schema(example = """
    {
      "username": "john",
      "email": "john@example.com"
    }
    """)
```

### 4. Hide Internal Endpoints

```java
@Hidden  // Exclude from API docs
@GetMapping("/internal/debug")
public String debug() { ... }
```

### 5. Secure Production

Disable Swagger UI in production or require authentication:

```java
.authorizeHttpRequests(auth -> auth
    .requestMatchers("/swagger-ui/**").hasRole("ADMIN")
)
```

## Troubleshooting

### Swagger UI Not Loading

**Problem:** 404 error when accessing `/swagger-ui.html`

**Solutions:**
1. Check dependency is in `build.gradle`
2. Verify security configuration allows public access
3. Check `springdoc.swagger-ui.enabled=true`
4. Try accessing `/swagger-ui/index.html` instead

### JWT Authentication Not Working

**Problem:** "Unauthorized" error after entering token

**Solutions:**
1. Verify token is valid (check expiration)
2. Ensure token is entered WITHOUT "Bearer " prefix
3. Check security configuration includes `@SecurityRequirement`
4. Test token with curl first

### OpenAPI Spec Empty

**Problem:** `/v3/api-docs` returns empty or minimal spec

**Solutions:**
1. Add `@Tag` annotations to controllers
2. Use `@Operation` on endpoints
3. Check package scanning configuration
4. Verify controllers are in `com.heimdall` package

### Rate Limit Headers Not Showing

**Problem:** Rate limit headers not in Swagger responses

**Solutions:**
1. Headers are added by interceptor, not visible in Swagger
2. Test with actual HTTP requests to see headers
3. Add `@ApiResponse` with `headers` parameter to document

## Export OpenAPI Spec

### JSON Format

```bash
curl http://localhost:8080/v3/api-docs -o api-spec.json
```

### YAML Format

```bash
curl http://localhost:8080/v3/api-docs.yaml -o api-spec.yaml
```

### Generate Client SDK

Use the exported spec with OpenAPI Generator:

```bash
# Generate Java client
openapi-generator-cli generate -i api-spec.yaml -g java -o client-java

# Generate Python client
openapi-generator-cli generate -i api-spec.yaml -g python -o client-python

# Generate TypeScript client
openapi-generator-cli generate -i api-spec.yaml -g typescript-axios -o client-ts
```

## Integration with CI/CD

### Validate OpenAPI Spec

```yaml
# .github/workflows/ci-cd.yml
- name: Validate OpenAPI Spec
  run: |
    ./gradlew bootRun &
    sleep 30
    curl -f http://localhost:8080/v3/api-docs || exit 1
```

### Publish API Documentation

```yaml
- name: Generate API Docs
  run: |
    curl http://localhost:8080/v3/api-docs -o openapi.json
    
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

## Related Documentation

- [JWT Authentication](JWT_AUTHENTICATION.md)
- [Circuit Breaker](CIRCUIT_BREAKER.md)
- [Rate Limiting](RATE_LIMITING.md) (coming soon)
- [SpringDoc OpenAPI](https://springdoc.org/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

## Support

For issues or questions:
- Check SpringDoc documentation: https://springdoc.org/
- Review controller annotations
- Test with curl before using Swagger UI
- Contact: DevOps Team
