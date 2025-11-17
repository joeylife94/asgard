# Contributing to Asgard

Thank you for your interest in contributing to Asgard! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and encourage diverse perspectives
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Ensure you have installed:
- Java 17+
- Gradle 8.5+
- Docker & Docker Compose
- Python 3.9+ (for Bifrost)
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/asgard.git
   cd asgard
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/joeylife94/asgard.git
   ```

### Setup Development Environment

1. Start infrastructure:
   ```powershell
   ./start-dev.ps1
   ```

2. Build the project:
   ```powershell
   ./gradlew build
   ```

3. Run tests:
   ```powershell
   ./gradlew test
   ```

## 🔄 Development Workflow

### Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Make Changes

1. Write your code
2. Add tests for new functionality
3. Ensure all tests pass: `./gradlew test`
4. Update documentation if needed

### Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

## 💻 Coding Standards

### Java/Spring Boot (Heimdall)

- Follow [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- Use meaningful variable and method names
- Add Javadoc comments for public APIs
- Keep methods small and focused (< 50 lines)
- Use Lombok annotations where appropriate
- Follow SOLID principles

**Example:**
```java
/**
 * Processes user authentication requests.
 *
 * @param request the authentication request
 * @return authentication response with JWT token
 * @throws AuthenticationException if credentials are invalid
 */
@Override
public AuthResponse authenticate(AuthRequest request) {
    // Implementation
}
```

### Python (Bifrost)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for function parameters and returns
- Add docstrings for classes and functions
- Maximum line length: 88 characters (Black formatter)
- Use meaningful variable names

**Example:**
```python
def process_prediction(data: Dict[str, Any]) -> PredictionResult:
    """
    Process ML prediction request.
    
    Args:
        data: Input data dictionary containing features
        
    Returns:
        PredictionResult containing prediction and confidence
        
    Raises:
        ValidationError: If input data is invalid
    """
    # Implementation
```

### Gradle Build Scripts

- Use Kotlin DSL or Groovy consistently
- Keep dependencies organized and commented
- Use version catalogs for dependency management
- Document custom tasks

## 📝 Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples

```bash
feat(heimdall): add JWT token refresh endpoint

Implement token refresh mechanism to allow users to obtain
new access tokens without re-authentication.

Closes #123
```

```bash
fix(bifrost): resolve memory leak in model inference

Fixed memory leak caused by not properly releasing
model resources after prediction.
```

```bash
docs(readme): update architecture diagram

Added detailed system architecture diagram showing
service interactions and data flow.
```

## 🔀 Pull Request Process

### Before Submitting

1. ✅ All tests pass: `./gradlew test`
2. ✅ Code follows style guidelines
3. ✅ Documentation is updated
4. ✅ Commit messages follow convention
5. ✅ Branch is up to date with main

### Submitting PR

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create Pull Request on GitHub

3. Fill out the PR template:
   - **Title**: Clear, concise description
   - **Description**: What changes were made and why
   - **Related Issues**: Link to related issues
   - **Screenshots**: If applicable
   - **Checklist**: Confirm all items

### PR Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged
- Your contribution will be acknowledged

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## 🧪 Testing

### Running Tests

```powershell
# All tests
./gradlew test

# Specific module
./gradlew :heimdall:test

# With coverage
./gradlew test jacocoTestReport

# Integration tests
./gradlew integrationTest
```

### Writing Tests

- Write unit tests for all new code
- Aim for >80% code coverage
- Use meaningful test names
- Follow Arrange-Act-Assert pattern
- Mock external dependencies

**Example:**
```java
@Test
@DisplayName("Should successfully authenticate user with valid credentials")
void shouldAuthenticateUserWithValidCredentials() {
    // Arrange
    AuthRequest request = new AuthRequest("user", "password");
    when(userService.findByUsername("user")).thenReturn(validUser);
    
    // Act
    AuthResponse response = authService.authenticate(request);
    
    // Assert
    assertThat(response.getToken()).isNotNull();
    assertThat(response.isSuccess()).isTrue();
}
```

## 📚 Additional Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Gradle User Guide](https://docs.gradle.org/current/userguide/userguide.html)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Project Architecture Docs](docs/)

## 💬 Communication

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussions
- **Pull Requests**: For code contributions

## 🏆 Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing to Asgard! 🚀
