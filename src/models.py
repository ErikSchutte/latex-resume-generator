"""Data models for resume information using Pydantic."""

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
from datetime import date
from typing import Optional


class ContactInfo(BaseModel):
    """Contact information for the resume."""

    name: str
    email: EmailStr
    phone: str
    linkedin: HttpUrl | None = None
    github: HttpUrl | None = None
    location: str
    position_title: str = "Cloud Solutions Architect"  # Default for tech roles

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format (E.164-compatible)."""
        import re

        # Remove common separators
        cleaned = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        # Allow optional + prefix and 10-15 digits
        pattern = r"^\+?[1-9]\d{9,14}$"
        if not re.match(pattern, cleaned):
            raise ValueError(
                "Invalid phone number format. Use international format: +1234567890"
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class Experience(BaseModel):
    """Professional experience entry."""

    company: str
    role: str
    location: str
    start_date: date
    end_date: date | None = None  # None indicates current position
    achievements: list[str]

    @field_validator("achievements")
    @classmethod
    def validate_achievements(cls, v: list[str]) -> list[str]:
        """Validate achievements list."""
        if len(v) < 2:
            raise ValueError("Include at least 2 achievements per role")
        if any(len(achievement) > 250 for achievement in v):
            raise ValueError("Achievement descriptions should be under 250 characters")
        if any(not achievement.strip() for achievement in v):
            raise ValueError("Achievements cannot be empty")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date | None, info) -> date | None:
        """Validate date range is logical."""
        if v and "start_date" in info.data:
            start_date = info.data["start_date"]
            if v < start_date:
                raise ValueError("End date cannot be before start date")
            if v > date.today():
                raise ValueError("End date cannot be in the future")
        return v

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        """Validate start date is reasonable."""
        if v > date.today():
            raise ValueError("Start date cannot be in the future")
        # Reasonable career start (not before 1970)
        if v.year < 1970:
            raise ValueError("Start date seems unreasonably old")
        return v


class Certification(BaseModel):
    """Professional certification."""

    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate certification date."""
        return v


class Education(BaseModel):
    """Education entry."""

    degree: str
    institution: str
    year: int
    gpa: str | None = None
    honors: str | None = None

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate graduation year."""
        current_year = date.today().year
        if v > current_year + 10:  # Allow future dates for expected graduation
            raise ValueError("Graduation year seems too far in the future")
        if v < 1950:
            raise ValueError("Graduation year seems unreasonably old")
        return v


class Language(BaseModel):
    """Language proficiency."""

    language: str
    proficiency: str


class ResumeData(BaseModel):
    """Complete resume data structure."""

    contact: ContactInfo
    summary: str
    experience: list[Experience]
    skills: dict[str, list[str]]  # category -> list of skills
    education: list[Education]
    certifications: list[Certification] = []
    languages: list[Language] = []
    interests: list[str] = []

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        """Validate professional summary."""
        v = v.strip()
        if len(v) < 50:
            raise ValueError("Summary should be at least 50 characters")
        if len(v) > 500:
            raise ValueError("Summary should not exceed 500 characters")
        return v

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, v: list[Experience]) -> list[Experience]:
        """Validate experience list."""
        if len(v) < 1:
            raise ValueError("Include at least one professional experience")
        return v

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: dict[str, list[str]]) -> dict[str, list[str]]:
        """Validate skills dictionary."""
        if not v:
            raise ValueError("Include at least one skill category")
        for category, skills in v.items():
            if not skills:
                raise ValueError(f"Skill category '{category}' cannot be empty")
        return v

    @field_validator("education")
    @classmethod
    def validate_education(cls, v: list[Education]) -> list[Education]:
        """Validate education list."""
        if len(v) < 1:
            raise ValueError("Include at least one education entry")
        return v
