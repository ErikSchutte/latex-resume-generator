"""LaTeX resume generator using Jinja2 templates."""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from datetime import date
from models import ResumeData
from validators import escape_latex, format_date, format_date_range


class LaTeXGenerator:
    """Generate LaTeX resume files from structured data."""

    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the LaTeX generator.

        Args:
            template_dir: Directory containing LaTeX templates
        """
        self.template_dir = Path(template_dir)

        # Configure Jinja2 with custom delimiters to avoid LaTeX conflicts
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape([]),  # No auto-escaping, we'll do it manually
            block_start_string="<BLOCK>",
            block_end_string="</BLOCK>",
            variable_start_string="<VAR>",
            variable_end_string="</VAR>",
            comment_start_string="<#",
            comment_end_string="#>",
        )

        # Register custom filters
        self.env.filters["latex_escape"] = escape_latex
        self.env.filters["format_date"] = self._format_date_filter
        self.env.filters["format_date_range"] = self._format_date_range_filter

    def _format_date_filter(self, d: date | None) -> str:
        """Jinja2 filter for formatting dates."""
        return format_date(d)

    def _format_date_range_filter(self, start: date, end: date | None = None) -> str:
        """Jinja2 filter for formatting date ranges."""
        return format_date_range(start, end)

    def _sort_experience(self, experience: list) -> list:
        """
        Sort experience entries by date, most recent first.

        Args:
            experience: List of experience entries

        Returns:
            Sorted list
        """
        return sorted(
            experience,
            key=lambda x: x.end_date if x.end_date else date.today(),
            reverse=True,
        )

    def _sort_certifications(self, certifications: list) -> list:
        """
        Sort certifications by date, most recent first.

        Args:
            certifications: List of certifications

        Returns:
            Sorted list
        """
        return sorted(certifications, key=lambda x: x.date if x.date else "", reverse=True)

    def _sort_education(self, education: list) -> list:
        """
        Sort education entries by year, most recent first.

        Args:
            education: List of education entries

        Returns:
            Sorted list
        """
        return sorted(education, key=lambda x: x.year, reverse=True)

    def generate(self, data: ResumeData, output_path: str | Path) -> Path:
        """
        Generate a LaTeX resume file from structured data.

        Args:
            data: Resume data model
            output_path: Path where the .tex file will be saved

        Returns:
            Path to the generated .tex file
        """
        # Load the template
        template = self.env.get_template("awesome-cv-tech/resume_template.tex.jinja2")

        # Prepare context for template
        context = {
            "contact": data.contact,
            "summary": data.summary,
            "experience": self._sort_experience(data.experience),
            "skills": data.skills,
            "certifications": self._sort_certifications(data.certifications),
            "education": self._sort_education(data.education),
            "interests": data.interests if hasattr(data, 'interests') else [],
            "languages": data.languages if hasattr(data, 'languages') else [],
            "has_certifications": len(data.certifications) > 0,
            "has_languages": hasattr(data, 'languages') and len(data.languages) > 0,
            "has_github": data.contact.github is not None,
            "has_linkedin": data.contact.linkedin is not None,
        }

        # Render the template
        latex_content = template.render(**context)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(latex_content, encoding="utf-8")

        return output_file

    def generate_from_dict(self, data_dict: dict, output_path: str | Path) -> Path:
        """
        Generate a LaTeX resume file from a dictionary.

        Args:
            data_dict: Dictionary containing resume data
            output_path: Path where the .tex file will be saved

        Returns:
            Path to the generated .tex file
        """
        # Validate and convert to ResumeData model
        data = ResumeData(**data_dict)
        return self.generate(data, output_path)
