"""pytest 설정"""

import pytest
from pathlib import Path
from bifrost.database import Database


@pytest.fixture(scope="session")
def test_db():
    """테스트용 DB"""
    db = Database("sqlite:///:memory:")
    db.init_db()
    yield db
    db.drop_all()


@pytest.fixture
def sample_log():
    """샘플 로그"""
    return """
2024-10-25 10:15:32 INFO  [main] Application starting...
2024-10-25 10:15:33 ERROR [main] Failed to connect to database
java.sql.SQLException: Connection refused
    at org.postgresql.Driver.connect(Driver.java:123)
"""


@pytest.fixture
def sample_log_file(tmp_path):
    """샘플 로그 파일"""
    log_file = tmp_path / "test.log"
    log_file.write_text("""
2024-10-25 10:15:32 INFO  [main] Application starting...
2024-10-25 10:15:33 ERROR [main] Connection failed
""")
    return log_file
