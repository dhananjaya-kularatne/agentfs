import pytest
from app.config import settings


@pytest.fixture(autouse=True)
def isolated_sandbox(tmp_path, monkeypatch):
    """Point every test at a fresh, isolated temp directory instead of the real sandbox."""
    monkeypatch.setattr(settings, "agent_working_directory", str(tmp_path))

    (tmp_path / "test.txt").write_text("This is a test file for AgentFS.", encoding="utf-8")
    (tmp_path / "meeting_notes.txt").write_text("Meeting notes from Monday.", encoding="utf-8")
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "q1_summary.txt").write_text("Q1 financial summary.", encoding="utf-8")

    yield tmp_path

