"""Tests for error message consistency."""

from src.messages import ErrorMessages, SuccessMessages, InfoMessages


def test_error_messages_have_emoji():
    """Test that all error messages start with emoji prefix."""
    for attr_name in dir(ErrorMessages):
        if not attr_name.startswith("_"):
            message = getattr(ErrorMessages, attr_name)
            assert message.startswith("❌"), f"{attr_name} should start with ❌"


def test_success_messages_have_emoji():
    """Test that all success messages start with emoji prefix."""
    for attr_name in dir(SuccessMessages):
        if not attr_name.startswith("_"):
            message = getattr(SuccessMessages, attr_name)
            assert message.startswith("✅"), f"{attr_name} should start with ✅"


def test_info_messages_have_emoji():
    """Test that all info messages start with emoji prefix."""
    for attr_name in dir(InfoMessages):
        if not attr_name.startswith("_"):
            message = getattr(InfoMessages, attr_name)
            assert message.startswith("ℹ️"), f"{attr_name} should start with ℹ️"


def test_error_messages_not_empty():
    """Test that error messages are not empty."""
    assert ErrorMessages.EMPTY_NAME
    assert ErrorMessages.INVALID_EMAIL
    assert ErrorMessages.INVALID_PHONE
    assert ErrorMessages.SUMMARY_TOO_SHORT


def test_success_messages_not_empty():
    """Test that success messages are not empty."""
    assert SuccessMessages.CONTACT_COMPLETE
    assert SuccessMessages.RESUME_COMPLETE


def test_message_formatting():
    """Test that template messages have proper format strings."""
    assert "{count}" in SuccessMessages.EXPERIENCE_ADDED
    assert "{category}" in SuccessMessages.SKILL_CATEGORY_ADDED
    assert "{count}" in SuccessMessages.CERTIFICATION_ADDED
