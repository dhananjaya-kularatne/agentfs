from app.tools.destructive_tools import write_file


def test_write_failure_message_does_not_leak_absolute_host_path(working_directory):
    # Make the intended parent a regular file so mkdir/write raises OSError.
    (working_directory / "blocker").write_text("i am a file", encoding="utf-8")

    result = write_file("blocker/child.txt", "data", working_directory)

    assert result["success"] is False
    assert result["error"]["type"] == "write_failed"
    message = result["error"]["message"]
    # The caller-supplied relative path is fine to echo; the resolved sandbox
    # location on disk is not.
    assert "blocker/child.txt" in message
    assert str(working_directory) not in message
