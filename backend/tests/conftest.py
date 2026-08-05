import pytest
from pathlib import Path


@pytest.fixture
def working_directory(tmp_path):
    """
    Provides an isolated, pre-seeded sandbox directory for each test,
    passed explicitly to tool functions rather than read from global config.
    """
    (tmp_path / "test.txt").write_text("This is a test file for AgentFS.", encoding="utf-8")
    (tmp_path / "meeting_notes.txt").write_text("Meeting notes from Monday.", encoding="utf-8")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "q1_summary.txt").write_text("Q1 financial summary.", encoding="utf-8")
    return tmp_path