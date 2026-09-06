import pytest

from app.tools.path_validator import validate_client_id, ClientIdValidationError
from app.services.agent_service import get_client_working_directory


# --- validate_client_id: the pure guard -------------------------------------

def test_accepts_a_uuid_style_id():
    cid = "3f2504e0-4f89-41d3-9a0c-0305e82c3301"
    assert validate_client_id(cid) == cid


def test_accepts_letters_digits_hyphen_underscore():
    assert validate_client_id("Client_01-abcDEF") == "Client_01-abcDEF"


@pytest.mark.parametrize("bad", [
    "../../../../etc",
    "..\\..\\Windows\\Temp",
    "a/b",
    "a\\b",
    "C:/Windows/Temp",
    "..",
    ".",
    "",
    "short",                       # under 8 chars
    "x" * 129,                     # over 128 chars
    "has space",
    "has.dot",
    "trailing\x00null",
    "colon:name",
])
def test_rejects_unsafe_or_malformed_ids(bad):
    with pytest.raises(ClientIdValidationError):
        validate_client_id(bad)


# --- get_client_working_directory: the sandbox root cannot be relocated -----

@pytest.fixture
def sandbox_base(tmp_path, monkeypatch):
    base = tmp_path / "sandbox"
    base.mkdir()
    monkeypatch.setattr(
        "app.services.agent_service.settings.agent_working_directory", str(base)
    )
    return base


def test_valid_client_gets_its_own_seeded_dir(sandbox_base):
    client_dir = get_client_working_directory("valid-client-1234")
    assert client_dir.parent == sandbox_base.resolve()
    assert client_dir.name == "valid-client-1234"
    assert (client_dir / "test.txt").exists()


@pytest.mark.parametrize("attack", [
    "../../../../../../etc",
    "..\\..\\..\\Windows",
    "C:/Windows/Temp",
    "",
])
def test_traversal_and_absolute_client_ids_are_rejected(sandbox_base, attack):
    with pytest.raises(ClientIdValidationError):
        get_client_working_directory(attack)
    # Nothing was created outside (or at) the sandbox base.
    assert list(sandbox_base.iterdir()) == []


def test_empty_client_id_cannot_target_the_shared_base(sandbox_base):
    with pytest.raises(ClientIdValidationError):
        get_client_working_directory("")
