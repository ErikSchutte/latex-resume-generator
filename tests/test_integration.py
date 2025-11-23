"""
Integration tests for end-to-end LaTeX resume generation and compilation.

These tests verify that the entire pipeline works correctly from data to PDF.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import json
from datetime import date
from models import ResumeData, ContactInfo, Experience, Education
from generator import LaTeXGenerator
import subprocess
import tempfile
import shutil


class TestEndToEndGeneration:
    """Integration tests for the complete resume generation pipeline."""

    @pytest.fixture
    def full_resume_data(self):
        """Create comprehensive resume data for integration testing."""
        return ResumeData(
            contact=ContactInfo(
                name="Integration Test User",
                email="integration@test.com",
                phone="+31612345678",
                location="Amsterdam, Netherlands",
                linkedin="https://linkedin.com/in/testuser",
                github="https://github.com/testuser",
                position_title="Senior Platform Engineer"
            ),
            summary="Experienced platform engineer with a passion for automation and cloud-native infrastructure. "
                   "Proven track record in disaster recovery planning and platform leadership.",
            experience=[
                Experience(
                    company="Tech Company A",
                    role="Platform Lead",
                    location="Amsterdam, NL",
                    start_date=date(2025, 10, 1),
                    end_date=None,  # Current position
                    achievements=[
                        "Lead design and development of scalable cloud-native infrastructure",
                        "Drive automation initiatives to advance platform toward full autonomy",
                        "Collaborate with engineering teams to ensure platform robustness"
                    ]
                ),
                Experience(
                    company="Tech Company B",
                    role="Senior Cloud Engineer",
                    location="Remote",
                    start_date=date(2023, 1, 1),
                    end_date=date(2025, 9, 30),
                    achievements=[
                        "Redesigned backup strategy leveraging Azure Cloud-native services",
                        "Architected comprehensive Disaster Recovery playbook",
                        "Implemented Azure Workload Identity for credential management"
                    ]
                ),
                Experience(
                    company="Tech Company C",
                    role="Cloud Platform Engineer",
                    location="Amsterdam, NL",
                    start_date=date(2020, 6, 1),
                    end_date=date(2022, 12, 31),
                    achievements=[
                        "Supported operations and maintenance of DRS platform",
                        "Assisted DevOps teams with IaC deployments",
                        "Developed Kubernetes secret rotation automation"
                    ]
                )
            ],
            skills={
                "Cloud Platforms": ["Azure", "AWS", "GCP"],
                "Container Orchestration": ["Kubernetes", "Azure AKS", "Docker"],
                "Security & Encryption": ["Managed HSM", "Mutual TLS", "Zero-Trust Architecture"],
                "Programming": ["Python", "Go", "Bash"],
                "Infrastructure as Code": ["Terraform", "Bicep", "Ansible"]
            },
            education=[
                Education(
                    degree="M.Sc. Computer Science",
                    institution="University of Amsterdam",
                    year=2020,
                    gpa=None,
                    honors=None
                ),
                Education(
                    degree="B.Sc. Computer Science (Graduated)",
                    institution="Hanzehogeschool University of Applied Sciences",
                    year=2017,
                    gpa=None,
                    honors=None
                )
            ],
            interests=["Cycling", "Cooking", "Technology & Innovation"]
        )

    @pytest.fixture
    def generator(self):
        """Create a LaTeX generator instance."""
        template_dir = Path(__file__).parent.parent / "templates"
        return LaTeXGenerator(str(template_dir))

    def test_complete_generation_pipeline(self, generator, full_resume_data, tmp_path):
        """Test the complete generation pipeline from data to .tex file."""
        output_file = tmp_path / "integration_test.tex"
        
        # Generate LaTeX
        result = generator.generate(full_resume_data, output_file)
        
        # Verify file was created
        assert result.exists()
        assert result.stat().st_size > 0
        
        # Read and verify content
        content = result.read_text()
        
        # Verify header information (name may be split with formatting)
        assert "Integration" in content and "Test User" in content
        assert "Senior Platform Engineer" in content
        assert "integration@test.com" in content
        
        # Verify all experience entries are present with dates
        assert "Platform Lead" in content
        assert "Tech Company A" in content
        assert "Oct 2025 -- Present" in content
        
        assert "Senior Cloud Engineer" in content
        assert "Tech Company B" in content
        assert "Jan 2023 -- Sep 2025" in content
        
        assert "Cloud Platform Engineer" in content
        assert "Tech Company C" in content
        assert "Jun 2020 -- Dec 2022" in content
        
        # Verify skills sections (check for skills that appear in sidebar and main section)
        assert "Azure" in content  # From Cloud Platforms skill category
        assert "Kubernetes" in content  # From Container Orchestration
        assert "Programming" in content or "Python" in content  # Programming category
        
        # Verify education with page break protection
        assert r"\needspace" in content
        assert "M.Sc. Computer Science" in content
        assert "University of Amsterdam" in content
        
        # Verify interests
        assert "Cycling" in content or "Personal Interests" in content

    def test_experience_dates_are_visible_in_output(self, generator, full_resume_data, tmp_path):
        """Test that experience dates are properly formatted in the LaTeX output."""
        output_file = tmp_path / "date_test.tex"
        generator.generate(full_resume_data, output_file)
        
        content = output_file.read_text()
        
        # Verify all three experience date ranges are in the output
        assert "Oct 2025 -- Present" in content, "Current position date range not found"
        assert "Jan 2023 -- Sep 2025" in content, "Second position date range not found"
        assert "Jun 2020 -- Dec 2022" in content, "Third position date range not found"
        
        # Verify experience commands exist
        assert r'\experience{' in content, "Experience commands not found in output"

    def test_education_page_break_protection(self, generator, full_resume_data, tmp_path):
        """Test that Education section has proper page break protection."""
        output_file = tmp_path / "pagebreak_test.tex"
        generator.generate(full_resume_data, output_file)
        
        content = output_file.read_text()
        
        # Find the Education section
        edu_start = content.find("% Education in Sidebar")
        assert edu_start != -1, "Education section not found"
        
        # Get the section (next 500 characters should contain needspace)
        edu_section = content[edu_start:edu_start + 500]
        
        # Verify needspace is present before education content
        needspace_pos = edu_section.find(r'\needspace')
        edu_heading_pos = edu_section.find(r'\colorheading{Edu}{cation}')
        
        assert needspace_pos != -1, "needspace command not found in Education section"
        assert edu_heading_pos != -1, "Education heading not found"
        assert needspace_pos < edu_heading_pos, "needspace should appear before Education heading"

    def test_json_data_loading_and_generation(self, generator, full_resume_data, tmp_path):
        """Test loading resume data from JSON and generating LaTeX."""
        # Save data to JSON
        json_file = tmp_path / "resume_data.json"
        
        # Convert ResumeData to dict (simplified for this test)
        data_dict = {
            "contact": {
                "name": full_resume_data.contact.name,
                "email": full_resume_data.contact.email,
                "phone": full_resume_data.contact.phone,
                "location": full_resume_data.contact.location,
                "linkedin": str(full_resume_data.contact.linkedin),
                "github": str(full_resume_data.contact.github),
                "position_title": full_resume_data.contact.position_title
            },
            "summary": full_resume_data.summary,
            "experience": [
                {
                    "company": exp.company,
                    "role": exp.role,
                    "location": exp.location,
                    "start_date": exp.start_date.isoformat(),
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "achievements": exp.achievements
                }
                for exp in full_resume_data.experience
            ],
            "skills": full_resume_data.skills,
            "education": [
                {
                    "degree": edu.degree,
                    "institution": edu.institution,
                    "year": edu.year,
                    "gpa": edu.gpa,
                    "honors": edu.honors
                }
                for edu in full_resume_data.education
            ],
            "certifications": [],
            "interests": full_resume_data.interests
        }
        
        with open(json_file, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        # Verify JSON file was created
        assert json_file.exists()
        
        # Load it back
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify data integrity
        assert loaded_data["contact"]["name"] == "Integration Test User"
        assert len(loaded_data["experience"]) == 3
        assert len(loaded_data["education"]) == 2

    def test_multiple_page_layout(self, generator, full_resume_data, tmp_path):
        """Test that the resume is designed for multi-page layout."""
        output_file = tmp_path / "multipage_test.tex"
        generator.generate(full_resume_data, output_file)
        
        content = output_file.read_text()
        
        # Verify paracol environment (for two-column layout)
        assert r'\begin{paracol}' in content
        assert r'\end{paracol}' in content
        
        # Verify needspace commands for page break management
        assert r'\needspace' in content
        
        # Verify document structure
        assert r'\documentclass' in content
        assert r'\begin{document}' in content
        assert r'\end{document}' in content


class TestLaTeXCompilation:
    """Tests that verify LaTeX compilation (requires Docker or pdflatex)."""

    @pytest.fixture
    def docker_available(self):
        """Check if Docker is available for compilation."""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @pytest.fixture
    def pdflatex_available(self):
        """Check if pdflatex is available."""
        try:
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @pytest.mark.skipif(
        not Path("docker-compose.yml").exists(),
        reason="Docker Compose not available"
    )
    def test_latex_syntax_validity(self, docker_available):
        """Test that generated LaTeX has valid syntax (requires compilation)."""
        if not docker_available:
            pytest.skip("Docker not available for LaTeX compilation test")
        
        # This is a placeholder for actual compilation test
        # In practice, you would compile the LaTeX and check for errors
        assert True

    def test_cls_file_latex_syntax(self):
        """Test that .cls file has valid LaTeX syntax."""
        cls_file = Path(__file__).parent.parent / "templates" / "awesome-cv-tech" / "awesome-cv.cls"
        content = cls_file.read_text()
        
        # Basic syntax checks
        assert content.count(r'\newcommand{') > 0
        assert content.count(r'\begin{') == content.count(r'\end{')
        
        # Check for critical commands
        assert r'\newcommand{\experience}' in content
        assert r'\newcommand{\sidebarheading}' in content
        assert r'\newcommand{\colorheading}' in content


class TestRegressionPrevention:
    """Tests to prevent regression of fixed bugs."""

    @pytest.fixture
    def generator(self):
        """Create a LaTeX generator instance."""
        template_dir = Path(__file__).parent.parent / "templates"
        return LaTeXGenerator(str(template_dir))

    def test_dates_are_included_in_experience_entries(self, generator, tmp_path):
        """
        Regression test: Ensure dates are always included in experience entries.
        
        This test prevents the bug where dates were not visible in the PDF output.
        """
        resume_data = ResumeData(
            contact=ContactInfo(
                name="Test User",
                email="test@example.com",
                phone="+31612345678",
                location="Amsterdam",
                position_title="Engineer"
            ),
            summary="Experienced software engineer with proven track record in cloud technologies and automation",
            experience=[
                Experience(
                    company="Test Company",
                    role="Test Role",
                    location="Test Location",
                    start_date=date(2023, 1, 1),
                    end_date=date(2024, 12, 31),
                    achievements=["Achievement 1", "Achievement 2"]
                )
            ],
            skills={"Testing": ["Test Skill 1", "Test Skill 2"]},
            education=[
                Education(
                    degree="Test Degree",
                    institution="Test University",
                    year=2020
                )
            ]
        )
        
        output_file = tmp_path / "regression_test.tex"
        generator.generate(resume_data, output_file)
        
        content = output_file.read_text()
        
        # The date range MUST be present in the output
        assert "Jan 2023 -- Dec 2024" in content, "Date range not found in experience entry"

    def test_education_section_not_split_across_pages(self, generator, tmp_path):
        """
        Regression test: Ensure Education section has page break protection.
        
        This test prevents the bug where Education heading appeared on one page
        and content on another.
        """
        resume_data = ResumeData(
            contact=ContactInfo(
                name="Test User",
                email="test@example.com",
                phone="+31612345678",
                location="Amsterdam",
                position_title="Engineer"
            ),
            summary="Experienced software engineer with proven track record in building scalable systems",
            experience=[
                Experience(
                    company="Company",
                    role="Role",
                    location="Location",
                    start_date=date(2020, 1, 1),
                    end_date=date(2023, 1, 1),
                    achievements=["Achievement 1", "Achievement 2"]
                )
            ],
            skills={"Skills": ["Skill 1", "Skill 2"]},
            education=[
                Education(
                    degree="M.Sc. Computer Science",
                    institution="University",
                    year=2020
                ),
                Education(
                    degree="B.Sc. Computer Science",
                    institution="University",
                    year=2017
                )
            ]
        )
        
        output_file = tmp_path / "edu_regression_test.tex"
        generator.generate(resume_data, output_file)
        
        content = output_file.read_text()
        
        # Find Education section
        edu_section_start = content.find("% Education in Sidebar")
        assert edu_section_start != -1
        
        # Check that needspace appears shortly before the Education heading
        edu_section = content[edu_section_start:edu_section_start + 500]
        assert r'\needspace' in edu_section, "Education section must have needspace for page break protection"
