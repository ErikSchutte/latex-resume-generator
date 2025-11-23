"""Tests for data models and validation."""

import pytest
from datetime import date
from pydantic import ValidationError
from src.models import ContactInfo, Experience, Certification, Education, ResumeData


def test_contact_info_valid():
    """Test valid contact information."""
    contact = ContactInfo(
        name="John Doe",
        email="john@example.com",
        phone="+12345678901",
        location="San Francisco, CA",
    )
    assert contact.name == "John Doe"
    assert contact.phone == "+12345678901"
    assert contact.position_title == "Cloud Solutions Architect"  # Default


def test_contact_info_with_position_title():
    """Test contact information with custom position title."""
    contact = ContactInfo(
        name="Jane Smith",
        email="jane@example.com",
        phone="+12345678901",
        location="Seattle, WA",
        position_title="Senior DevOps Engineer",
    )
    assert contact.position_title == "Senior DevOps Engineer"


def test_contact_info_invalid_email():
    """Test invalid email raises validation error."""
    with pytest.raises(ValidationError):
        ContactInfo(
            name="John Doe",
            email="invalid-email",
            phone="+12345678901",
            location="San Francisco, CA",
        )


def test_contact_info_invalid_phone():
    """Test invalid phone number raises validation error."""
    with pytest.raises(ValidationError):
        ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="123",  # Too short
            location="San Francisco, CA",
        )


def test_experience_valid():
    """Test valid experience entry."""
    exp = Experience(
        company="Tech Corp",
        role="Software Engineer",
        location="Seattle, WA",
        start_date=date(2020, 1, 1),
        end_date=date(2023, 12, 31),
        achievements=[
            "Built scalable systems serving 1M+ users",
            "Led team of 5 engineers",
        ],
    )
    assert exp.company == "Tech Corp"
    assert len(exp.achievements) == 2


def test_experience_invalid_dates():
    """Test invalid date range raises validation error."""
    with pytest.raises(ValidationError):
        Experience(
            company="Tech Corp",
            role="Software Engineer",
            location="Seattle, WA",
            start_date=date(2023, 1, 1),
            end_date=date(2020, 1, 1),  # Before start date
            achievements=["Achievement 1", "Achievement 2"],
        )


def test_experience_too_few_achievements():
    """Test too few achievements raises validation error."""
    with pytest.raises(ValidationError):
        Experience(
            company="Tech Corp",
            role="Software Engineer",
            location="Seattle, WA",
            start_date=date(2020, 1, 1),
            achievements=["Only one"],  # Need at least 2
        )


def test_certification_valid():
    """Test valid certification."""
    cert = Certification(
        name="AWS Solutions Architect",
        issuer="Amazon Web Services",
        date=date(2023, 6, 1),
    )
    assert cert.name == "AWS Solutions Architect"


def test_education_valid():
    """Test valid education entry."""
    edu = Education(
        degree="Master of Science", institution="Stanford University", year=2020
    )
    assert edu.degree == "Master of Science"
    assert edu.year == 2020


def test_resume_data_valid():
    """Test valid complete resume data."""
    data = ResumeData(
        contact=ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="+12345678901",
            location="San Francisco, CA",
        ),
        summary="Experienced engineer with 10+ years building scalable cloud systems.",
        experience=[
            Experience(
                company="Tech Corp",
                role="Senior Engineer",
                location="Seattle, WA",
                start_date=date(2020, 1, 1),
                achievements=["Achievement 1", "Achievement 2"],
            )
        ],
        skills={"Cloud": ["AWS", "Azure"], "Programming": ["Python", "Go"]},
        education=[
            Education(degree="BS Computer Science", institution="MIT", year=2010)
        ],
    )
    assert data.contact.name == "John Doe"
    assert len(data.experience) == 1
    assert len(data.skills) == 2


def test_resume_data_invalid_summary():
    """Test invalid summary raises validation error."""
    with pytest.raises(ValidationError):
        ResumeData(
            contact=ContactInfo(
                name="John Doe",
                email="john@example.com",
                phone="+12345678901",
                location="San Francisco, CA",
            ),
            summary="Too short",  # Less than 50 characters
            experience=[
                Experience(
                    company="Tech Corp",
                    role="Engineer",
                    location="Seattle, WA",
                    start_date=date(2020, 1, 1),
                    achievements=["Achievement 1", "Achievement 2"],
                )
            ],
            skills={"Cloud": ["AWS"]},
            education=[Education(degree="BS", institution="MIT", year=2010)],
        )
