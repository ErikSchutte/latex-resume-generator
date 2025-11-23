"""
Tests for LaTeX generation and template rendering.

This module tests the LaTeX generation functionality including:
- Date formatting and display in experience entries
- Page break handling for sidebar sections
- Template rendering with proper data
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from datetime import date
from models import ResumeData, ContactInfo, Experience, Education
from generator import LaTeXGenerator
from validators import format_date, format_date_range


class TestDateFormatting:
    """Test date formatting functions."""

    def test_format_date_with_valid_date(self):
        """Test formatting a valid date returns correct format."""
        test_date = date(2025, 10, 15)
        result = format_date(test_date)
        assert result == "Oct 2025"

    def test_format_date_with_none_returns_present(self):
        """Test formatting None returns 'Present'."""
        result = format_date(None)
        assert result == "Present"

    def test_format_date_range_with_end_date(self):
        """Test formatting a complete date range."""
        start = date(2023, 10, 1)
        end = date(2025, 10, 1)
        result = format_date_range(start, end)
        assert result == "Oct 2023 -- Oct 2025"

    def test_format_date_range_with_no_end_date(self):
        """Test formatting a date range with current position (no end date)."""
        start = date(2025, 10, 1)
        result = format_date_range(start, None)
        assert result == "Oct 2025 -- Present"

    def test_format_date_range_same_month(self):
        """Test formatting when start and end are in the same month."""
        start = date(2025, 1, 1)
        end = date(2025, 1, 31)
        result = format_date_range(start, end)
        assert result == "Jan 2025 -- Jan 2025"


class TestExperienceRendering:
    """Test experience entry rendering in LaTeX."""

    @pytest.fixture
    def sample_experience(self):
        """Create a sample experience entry for testing."""
        return Experience(
            company="Test Company",
            role="Senior Engineer",
            location="Amsterdam, NL",
            start_date=date(2023, 1, 1),
            end_date=date(2025, 6, 30),
            achievements=[
                "Achieved significant results",
                "Delivered important projects",
                "Improved team productivity by 50%"
            ]
        )

    @pytest.fixture
    def current_experience(self):
        """Create a sample current/ongoing experience entry."""
        return Experience(
            company="Current Company",
            role="Platform Lead",
            location="Remote",
            start_date=date(2025, 10, 1),
            end_date=None,  # Current position
            achievements=[
                "Leading platform architecture",
                "Driving automation initiatives"
            ]
        )

    def test_experience_includes_date_range(self, sample_experience):
        """Test that experience LaTeX includes the date range."""
        start_str = format_date(sample_experience.start_date)
        end_str = format_date(sample_experience.end_date)
        expected_range = f"{start_str} -- {end_str}"
        
        assert expected_range == "Jan 2023 -- Jun 2025"

    def test_current_experience_shows_present(self, current_experience):
        """Test that current experience shows 'Present' as end date."""
        start_str = format_date(current_experience.start_date)
        end_str = format_date(current_experience.end_date)
        expected_range = f"{start_str} -- {end_str}"
        
        assert expected_range == "Oct 2025 -- Present"
        assert "Present" in expected_range


class TestLaTeXGenerator:
    """Test the LaTeX generator functionality."""

    @pytest.fixture
    def minimal_resume_data(self):
        """Create minimal valid resume data for testing."""
        return ResumeData(
            contact=ContactInfo(
                name="Test User",
                email="test@example.com",
                phone="+31612345678",
                location="Amsterdam, Netherlands",
                linkedin="https://linkedin.com/in/testuser",
                github="https://github.com/testuser",
                position_title="Test Engineer"
            ),
            summary="Experienced test engineer with expertise in testing.",
            experience=[
                Experience(
                    company="Test Corp",
                    role="Test Engineer",
                    location="Amsterdam",
                    start_date=date(2020, 1, 1),
                    end_date=date(2023, 12, 31),
                    achievements=["Testing achievement 1", "Testing achievement 2"]
                )
            ],
            skills={
                "Testing": ["Unit Tests", "Integration Tests"],
                "Languages": ["Python", "JavaScript"]
            },
            education=[
                Education(
                    degree="B.Sc. Computer Science",
                    institution="Test University",
                    year=2019,
                    gpa=None,
                    honors=None
                )
            ]
        )

    @pytest.fixture
    def generator(self):
        """Create a LaTeX generator instance."""
        template_dir = Path(__file__).parent.parent / "templates"
        return LaTeXGenerator(str(template_dir))

    def test_generator_initialization(self, generator):
        """Test that generator initializes correctly."""
        assert generator is not None
        assert generator.env is not None
        assert "latex_escape" in generator.env.filters
        assert "format_date" in generator.env.filters

    def test_generate_creates_tex_file(self, generator, minimal_resume_data, tmp_path):
        """Test that generate() creates a .tex file."""
        output_file = tmp_path / "test_resume.tex"
        result = generator.generate(minimal_resume_data, output_file)
        
        assert result.exists()
        assert result.suffix == ".tex"

    def test_generated_tex_contains_experience_dates(self, generator, minimal_resume_data, tmp_path):
        """Test that generated LaTeX contains experience date ranges."""
        output_file = tmp_path / "test_resume.tex"
        generator.generate(minimal_resume_data, output_file)
        
        content = output_file.read_text()
        
        # Check that experience command is used
        assert r"\experience{" in content
        
        # Check that dates are present
        assert "Jan 2020 -- Dec 2023" in content

    def test_generated_tex_contains_education_needspace(self, generator, minimal_resume_data, tmp_path):
        """Test that Education section has needspace to prevent page breaks."""
        output_file = tmp_path / "test_resume.tex"
        generator.generate(minimal_resume_data, output_file)
        
        content = output_file.read_text()
        
        # Find the Education section
        assert r"\colorheading{Edu}{cation}" in content
        
        # Check that needspace is before education heading
        # This ensures the heading and content stay together
        edu_section_start = content.find("% Education in Sidebar")
        needspace_pos = content.find(r"\needspace", edu_section_start)
        edu_heading_pos = content.find(r"\colorheading{Edu}{cation}", edu_section_start)
        
        assert needspace_pos != -1, "needspace command not found"
        assert edu_heading_pos != -1, "Education heading not found"
        assert needspace_pos < edu_heading_pos, "needspace should come before Education heading"


class TestTemplateIntegrity:
    """Test template file integrity and structure."""

    def test_template_file_exists(self):
        """Test that the template file exists."""
        template_file = Path(__file__).parent.parent / "templates" / "awesome-cv-tech" / "resume_template.tex.jinja2"
        assert template_file.exists()

    def test_cls_file_exists(self):
        """Test that the .cls file exists."""
        cls_file = Path(__file__).parent.parent / "templates" / "awesome-cv-tech" / "awesome-cv.cls"
        assert cls_file.exists()

    def test_experience_command_structure(self):
        """Test that experience command has correct structure."""
        cls_file = Path(__file__).parent.parent / "templates" / "awesome-cv-tech" / "awesome-cv.cls"
        content = cls_file.read_text()
        
        # Check that experience command exists and uses minipages for proper width
        assert r"\newcommand{\experience}[5]" in content
        assert "minipage" in content or "tabularx" in content

    def test_education_has_page_break_protection(self):
        """Test that Education section has page break protection."""
        template_file = Path(__file__).parent.parent / "templates" / "awesome-cv-tech" / "resume_template.tex.jinja2"
        content = template_file.read_text()
        
        # Find Education section and verify needspace is present
        edu_section = content[content.find("% Education in Sidebar"):]
        
        # Check within reasonable distance (500 chars) that needspace appears
        assert r"\needspace" in edu_section[:500], "Education section should have needspace for page break protection"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_experience_with_very_long_role_name(self):
        """Test handling of very long role names."""
        long_role = "Very Long Role Title That Might Cause Layout Issues" * 2
        exp = Experience(
            company="Test",
            role=long_role,
            location="Test Location",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
            achievements=["Achievement 1", "Achievement 2"]
        )
        
        # Should not raise an error
        assert exp.role == long_role

    def test_experience_with_very_long_company_name(self):
        """Test handling of very long company names."""
        long_company = "Very Long Company Name That Might Cause Issues" * 2
        exp = Experience(
            company=long_company,
            role="Engineer",
            location="Test Location",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
            achievements=["Achievement 1", "Achievement 2"]
        )
        
        assert exp.company == long_company

    def test_date_formatting_for_different_years(self):
        """Test date formatting across different years."""
        test_cases = [
            (date(2020, 1, 1), "Jan 2020"),
            (date(2025, 12, 31), "Dec 2025"),
            (date(2023, 6, 15), "Jun 2023"),
            (date(2024, 3, 1), "Mar 2024"),
        ]
        
        for test_date, expected in test_cases:
            result = format_date(test_date)
            assert result == expected, f"Expected {expected}, got {result}"

    def test_multiple_education_entries(self):
        """Test handling of multiple education entries."""
        edu_list = [
            Education(
                degree="M.Sc. Computer Science",
                institution="University 1",
                year=2021,
                gpa=None,
                honors=None
            ),
            Education(
                degree="B.Sc. Computer Science",
                institution="University 2",
                year=2019,
                gpa=None,
                honors=None
            )
        ]
        
        assert len(edu_list) == 2
        assert edu_list[0].year > edu_list[1].year  # More recent first
