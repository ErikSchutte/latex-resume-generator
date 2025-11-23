"""Tests for conversation manager and prompts."""

import pytest
from datetime import date
from src.conversation import ConversationManager
from src.prompts import ConversationState, ConversationPrompts


def test_conversation_initial_state():
    """Test conversation starts in greeting state."""
    conv = ConversationManager()
    assert conv.state == ConversationState.GREETING
    assert conv.data["contact"] == {}
    assert conv.data["experience"] == []


def test_greeting_advances_to_contact():
    """Test greeting advances to contact name."""
    conv = ConversationManager()
    success, error = conv.process_input("")
    assert success
    assert conv.state == ConversationState.CONTACT_NAME


def test_contact_info_collection():
    """Test collecting contact information."""
    conv = ConversationManager()

    # Skip greeting
    conv.process_input("")

    # Name
    success, error = conv.process_input("John Doe")
    assert success
    assert conv.data["contact"]["name"] == "John Doe"
    assert conv.state == ConversationState.CONTACT_EMAIL

    # Email
    success, error = conv.process_input("john@example.com")
    assert success
    assert conv.data["contact"]["email"] == "john@example.com"
    assert conv.state == ConversationState.CONTACT_PHONE

    # Phone
    success, error = conv.process_input("+12345678901")
    assert success
    assert conv.data["contact"]["phone"] == "+12345678901"
    assert conv.state == ConversationState.CONTACT_LOCATION

    # Location
    success, error = conv.process_input("San Francisco, CA")
    assert success
    assert conv.data["contact"]["location"] == "San Francisco, CA"
    assert conv.state == ConversationState.CONTACT_LINKEDIN


def test_position_title_collection():
    """Test collecting position title with default and custom values."""
    conv = ConversationManager()
    conv.state = ConversationState.CONTACT_GITHUB

    # Skip GitHub
    success, _ = conv.process_input("")
    assert success
    assert conv.state == ConversationState.CONTACT_POSITION_TITLE

    # Test with custom position title
    success, _ = conv.process_input("Senior Cloud Architect")
    assert success
    assert conv.data["contact"]["position_title"] == "Senior Cloud Architect"
    assert conv.state == ConversationState.SUMMARY

    # Test with default (empty input)
    conv2 = ConversationManager()
    conv2.state = ConversationState.CONTACT_POSITION_TITLE
    success, _ = conv2.process_input("")
    assert success
    assert conv2.data["contact"]["position_title"] == "Cloud Solutions Architect"
    assert conv2.state == ConversationState.SUMMARY


def test_empty_name_fails():
    """Test empty name is rejected."""
    conv = ConversationManager()
    conv.process_input("")  # Skip greeting

    success, error = conv.process_input("")
    assert not success
    assert "empty" in error.lower()


def test_invalid_email_fails():
    """Test invalid email is rejected."""
    conv = ConversationManager()
    conv.process_input("")  # Skip greeting
    conv.process_input("John Doe")  # Name

    success, error = conv.process_input("not-an-email")
    assert not success
    assert "email" in error.lower()


def test_experience_collection():
    """Test collecting experience entry."""
    conv = ConversationManager()

    # Fast forward to experience section
    conv.state = ConversationState.EXPERIENCE_START

    # Company
    success, error = conv.process_input("Tech Corp")
    assert success
    assert conv.current_experience["company"] == "Tech Corp"
    assert conv.state == ConversationState.EXPERIENCE_ROLE

    # Role
    success, error = conv.process_input("Senior Engineer")
    assert success
    assert conv.current_experience["role"] == "Senior Engineer"

    # Location
    success, error = conv.process_input("Seattle, WA")
    assert success

    # Start date
    success, error = conv.process_input("2020-01-15")
    assert success
    assert conv.current_experience["start_date"] == "2020-01-15"

    # End date (current)
    success, error = conv.process_input("current")
    assert success
    assert conv.current_experience["end_date"] is None

    # First achievement
    success, error = conv.process_input("Led team of 5 engineers")
    assert success
    assert len(conv.achievements_buffer) == 1

    # Second achievement
    success, error = conv.process_input("Reduced costs by 40%")
    assert success
    assert len(conv.achievements_buffer) == 2

    # Finish achievements
    success, error = conv.process_input("")
    assert success
    assert len(conv.data["experience"]) == 1
    assert conv.data["experience"][0]["achievements"] == [
        "Led team of 5 engineers",
        "Reduced costs by 40%",
    ]


def test_experience_requires_two_achievements():
    """Test experience must have at least 2 achievements."""
    conv = ConversationManager()
    conv.state = ConversationState.EXPERIENCE_ACHIEVEMENTS
    conv.achievements_buffer = ["Only one achievement"]

    success, error = conv.process_input("")  # Try to finish with only 1
    assert not success
    assert "2 achievements" in error.lower()


def test_achievement_max_length():
    """Test achievement cannot exceed 250 characters."""
    conv = ConversationManager()
    conv.state = ConversationState.EXPERIENCE_ACHIEVEMENTS

    long_achievement = "a" * 251
    success, error = conv.process_input(long_achievement)
    assert not success
    assert "250 characters" in error


def test_skills_collection():
    """Test collecting skills by category."""
    conv = ConversationManager()
    conv.state = ConversationState.SKILLS

    # Skip intro
    success, error = conv.process_input("")
    assert success
    assert conv.state == ConversationState.SKILLS_CATEGORY


def test_skills_list_state_flow():
    """Test the new SKILLS_LIST state for proper skills collection."""
    conv = ConversationManager()
    conv.state = ConversationState.SKILLS_CATEGORY

    # Enter first category name
    success, error = conv.process_input("Cloud Platforms")
    assert success
    assert conv.state == ConversationState.SKILLS_LIST
    assert conv.current_category == "Cloud Platforms"

    # Enter skills for that category
    success, msg = conv.process_input("AWS, Azure, GCP")
    assert success
    assert "3 skills" in msg
    assert conv.state == ConversationState.SKILLS_CATEGORY
    assert len(conv.data["skills"]["Cloud Platforms"]) == 3
    assert conv.data["skills"]["Cloud Platforms"] == ["AWS", "Azure", "GCP"]
    assert conv.current_category == ""  # Should be cleared

    # Add another category
    success, _ = conv.process_input("Programming Languages")
    assert success
    assert conv.state == ConversationState.SKILLS_LIST
    assert conv.current_category == "Programming Languages"

    # Enter skills with extra whitespace
    success, msg = conv.process_input(" Python ,  Go  , TypeScript")
    assert success
    assert len(conv.data["skills"]["Programming Languages"]) == 3
    assert conv.data["skills"]["Programming Languages"] == [
        "Python",
        "Go",
        "TypeScript",
    ]

    # Test empty skills fails (and stays in SKILLS_LIST for retry)
    success, _ = conv.process_input("Empty Category")
    assert success
    assert conv.state == ConversationState.SKILLS_LIST
    success, error = conv.process_input("")
    assert not success
    assert "at least one skill" in error
    assert conv.state == ConversationState.SKILLS_LIST  # Should stay for retry

    # Provide valid skills after failure
    success, _ = conv.process_input("Docker, Kubernetes")
    assert success
    assert conv.state == ConversationState.SKILLS_CATEGORY
    assert len(conv.data["skills"]["Empty Category"]) == 2

    # Finish skills
    success, _ = conv.process_input("done")
    assert success
    assert conv.state == ConversationState.CERTIFICATIONS_START


def test_date_parsing():
    """Test date parsing utility."""
    prompts = ConversationPrompts()

    # Valid date
    d = prompts.parse_date("2020-01-15")
    assert d == date(2020, 1, 15)

    # Current position
    d = prompts.parse_date("current")
    assert d is None

    # Empty
    d = prompts.parse_date("")
    assert d is None

    # Invalid format
    with pytest.raises(ValueError):
        prompts.parse_date("2020/01/15")

    with pytest.raises(ValueError):
        prompts.parse_date("not-a-date")


def test_yes_no_parsing():
    """Test yes/no response parsing."""
    prompts = ConversationPrompts()

    assert prompts.parse_yes_no("yes") is True
    assert prompts.parse_yes_no("Yes") is True
    assert prompts.parse_yes_no("YES") is True
    assert prompts.parse_yes_no("y") is True
    assert prompts.parse_yes_no("Y") is True

    assert prompts.parse_yes_no("no") is False
    assert prompts.parse_yes_no("No") is False
    assert prompts.parse_yes_no("n") is False
    assert prompts.parse_yes_no("anything else") is False


def test_summary_length_validation():
    """Test summary must be 50-500 characters."""
    conv = ConversationManager()
    conv.state = ConversationState.SUMMARY

    # Too short
    success, error = conv.process_input("Too short")
    assert not success
    assert "50 characters" in error

    # Too long
    long_summary = "a" * 501
    success, error = conv.process_input(long_summary)
    assert not success
    assert "500 characters" in error

    # Just right
    valid_summary = "Cloud architect with 10+ years of experience in designing and implementing secure solutions."
    success, error = conv.process_input(valid_summary)
    assert success
    assert conv.data["summary"] == valid_summary


def test_certification_collection():
    """Test collecting certification."""
    conv = ConversationManager()
    conv.state = ConversationState.CERTIFICATION_NAME

    # Name
    success, error = conv.process_input("AWS Solutions Architect")
    assert success
    assert conv.current_certification["name"] == "AWS Solutions Architect"

    # Issuer
    success, error = conv.process_input("Amazon Web Services")
    assert success
    assert conv.current_certification["issuer"] == "Amazon Web Services"

    # Date
    success, error = conv.process_input("2023-06-15")
    assert success
    assert len(conv.data["certifications"]) == 1
    assert conv.data["certifications"][0]["date"] == "2023-06-15"


def test_education_collection():
    """Test collecting education."""
    conv = ConversationManager()
    conv.state = ConversationState.EDUCATION_DEGREE

    # Degree
    success, error = conv.process_input("Master of Science in Computer Science")
    assert success
    assert conv.current_education["degree"] == "Master of Science in Computer Science"

    # Institution
    success, error = conv.process_input("Stanford University")
    assert success
    assert conv.current_education["institution"] == "Stanford University"

    # Year
    success, error = conv.process_input("2020")
    assert success
    assert len(conv.data["education"]) == 1
    assert conv.data["education"][0]["year"] == 2020


def test_education_year_validation():
    """Test education year must be reasonable."""
    conv = ConversationManager()
    conv.state = ConversationState.EDUCATION_YEAR
    conv.current_education = {"degree": "BS", "institution": "MIT"}

    # Too old
    success, error = conv.process_input("1900")
    assert not success
    assert "unreasonable" in error.lower()

    # Too far in future
    success, error = conv.process_input("2050")
    assert not success

    # Invalid format
    success, error = conv.process_input("not a year")
    assert not success


def test_conversation_completion():
    """Test conversation can reach completion state."""
    conv = ConversationManager()
    conv.state = ConversationState.REVIEW
    conv.data = {
        "contact": {"name": "John", "email": "john@example.com"},
        "experience": [{}],
        "skills": {"Cloud": ["AWS"]},
        "certifications": [],
        "education": [{}],
    }

    # Approve review
    success, error = conv.process_input("yes")
    assert success
    assert conv.state == ConversationState.COMPLETE
    assert conv.is_complete()


def test_conversation_restart_from_review():
    """Test can restart conversation from review."""
    conv = ConversationManager()
    conv.state = ConversationState.REVIEW
    conv.data = {"contact": {"name": "Old Name"}}

    # Reject review
    success, error = conv.process_input("no")
    assert success
    assert conv.state == ConversationState.GREETING
    assert conv.data["contact"] == {}  # Reset
