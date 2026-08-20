# Testing Guide

## Overview

RAGForge uses pytest for backend testing and follows industry best practices for test coverage, integration testing, and continuous testing.

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_api.py              # API endpoint tests
├── test_ingestion.py        # Document processing tests
├── test_retrieval.py        # Retrieval pipeline tests
└── fixtures/                # Test data
    └── sample.pdf
```

## Running Tests

### Install Test Dependencies

```bash
cd backend
pip install pytest pytest-asyncio httpx
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestHealthEndpoint::test_health_check
```

### Run Tests in Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw
```

## Test Categories

### 1. Unit Tests

Test individual functions in isolation:

```python
# tests/test_ingestion.py
def test_generate_hash_consistent():
    """Same file should produce same hash"""
    # Test implementation
```

### 2. Integration Tests

Test multiple components together:

```python
# tests/test_api.py
def test_upload_document(client):
    """Test full upload pipeline"""
    # Test implementation
```

### 3. API Tests

Test FastAPI endpoints:

```python
# tests/test_api.py
def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
```

## Test Fixtures

### Available Fixtures

```python
# conftest.py fixtures

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def sample_pdf_path():
    """Path to sample test PDF"""
    return "tests/fixtures/sample.pdf"

@pytest.fixture
def mock_document_data():
    """Mock document metadata"""
    return {
        "document_id": "test123",
        "filename": "test.pdf",
        "pages": 5,
        "chunks": 25
    }
```

### Using Fixtures

```python
def test_with_client(client):
    """Test using FastAPI client fixture"""
    response = client.get("/api/health")
    assert response.status_code == 200

def test_with_mock_data(mock_document_data):
    """Test using mock data fixture"""
    assert mock_document_data["pages"] == 5
```

## Mocking

### Mock External Services

```python
from unittest.mock import Mock, patch

@patch('app.rag.generator.ChatOllama')
def test_llm_generation(mock_ollama):
    """Test with mocked Ollama"""
    mock_ollama.return_value.invoke.return_value = "Test answer"
    # Test implementation
```

### Mock File Operations

```python
def test_file_upload(tmp_path):
    """Test with temporary file"""
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"PDF content")
    # Test implementation
```

## Test Coverage

### Current Coverage

Run coverage report:

```bash
pytest --cov=app --cov-report=term --cov-report=html
```

View HTML report:

```bash
# Open htmlcov/index.html in browser
```

### Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| app/api/* | 80%+ | TBD |
| app/rag/* | 90%+ | TBD |
| app/database/* | 80%+ | TBD |
| Overall | 80%+ | TBD |

## Writing Tests

### Test Naming Convention

```python
# Good test names (descriptive)
def test_document_hash_is_consistent()
def test_empty_pdf_raises_error()
def test_chat_endpoint_returns_answer()

# Bad test names (vague)
def test_function()
def test_case1()
```

### Test Structure (AAA Pattern)

```python
def test_example():
    # Arrange - Set up test data
    test_data = {"key": "value"}
    
    # Act - Perform action
    result = function_to_test(test_data)
    
    # Assert - Verify result
    assert result == expected_value
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    """Test async function"""
    result = await async_function()
    assert result is not None
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Common Issues

### Issue: ChromaDB persistence errors

**Solution**: Use temporary directory for tests

```python
@pytest.fixture
def temp_chroma_dir(tmp_path):
    """Temporary ChromaDB directory"""
    return tmp_path / "chroma"
```

### Issue: Ollama not available in CI

**Solution**: Mock Ollama calls

```python
@patch('app.rag.generator.check_ollama_status')
def test_without_ollama(mock_status):
    mock_status.return_value = {"available": False}
    # Test implementation
```

### Issue: Slow tests

**Solution**: Use pytest-xdist for parallel execution

```bash
pip install pytest-xdist
pytest -n auto  # Run on all CPU cores
```

## Best Practices

### 1. Fast Tests
- Unit tests should run in milliseconds
- Integration tests should run in seconds
- Mock slow operations (LLM calls, embeddings)

### 2. Isolated Tests
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 3. Readable Tests
- Use descriptive test names
- Add docstrings explaining what's tested
- Use arrange-act-assert pattern

### 4. Coverage Over Quantity
- Aim for meaningful coverage, not 100%
- Focus on critical paths
- Test edge cases and error handling

### 5. Continuous Testing
- Run tests before commits
- Set up pre-commit hooks
- Use CI/CD for automated testing

## Test Data

### Creating Test PDFs

```python
from reportlab.pdfgen import canvas

def create_test_pdf(path: str, content: str):
    """Create a simple test PDF"""
    c = canvas.Canvas(path)
    c.drawString(100, 750, content)
    c.save()
```

### Sample Test Data

```python
SAMPLE_DOCUMENTS = [
    {
        "filename": "test1.pdf",
        "content": "Machine learning is a subset of AI.",
        "expected_chunks": 1
    },
    {
        "filename": "test2.pdf",
        "content": "Deep learning uses neural networks.",
        "expected_chunks": 1
    }
]
```

## Debugging Tests

### Run Single Test with Output

```bash
pytest tests/test_api.py::test_health_check -v -s
```

### Use pdb for Debugging

```python
def test_example():
    import pdb; pdb.set_trace()  # Breakpoint
    result = function_to_test()
    assert result == expected
```

### Print Debugging

```python
def test_with_prints():
    result = function_to_test()
    print(f"Result: {result}")  # Will show with -s flag
    assert result is not None
```

## Next Steps

1. **Add more test fixtures** for common scenarios
2. **Increase coverage** to 80%+
3. **Add performance tests** for retrieval speed
4. **Add load tests** for API endpoints
5. **Set up CI/CD** for automated testing
6. **Add mutation testing** (pytest-mutpy)
7. **Add property-based testing** (hypothesis)

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
