"""Command-line interface for the LaTeX Resume Generator."""

import click
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import ResumeData
from generator import LaTeXGenerator
from compiler import LaTeXCompiler


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    LaTeX Resume Generation System

    Create professional resumes for cloud architecture and technology leadership roles.
    """
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="output/",
    help="Output directory for generated files",
)
@click.option("--preview", is_flag=True, help="Open PDF after generation")
@click.option("--template", default="awesome-cv-tech", help="Template to use")
@click.option(
    "--latex-only", is_flag=True, help="Generate only .tex file, skip PDF compilation"
)
def generate(input_file, output, preview, template, latex_only):
    """Generate resume from JSON data file."""
    try:
        click.echo(f"📄 Loading resume data from {input_file}...")

        # Load and validate data
        with open(input_file, "r") as f:
            data_dict = json.load(f)

        data = ResumeData(**data_dict)
        click.secho("✓ Data validation passed", fg="green")

        # Generate LaTeX
        click.echo("\n📝 Generating LaTeX file...")
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tex_filename = f"resume_{timestamp}.tex"
        tex_path = output_dir / tex_filename

        generator = LaTeXGenerator("templates")
        generated_tex = generator.generate(data, tex_path)
        click.secho(f"✓ LaTeX file created: {generated_tex}", fg="green")

        if latex_only:
            click.echo("\n✅ LaTeX generation complete!")
            return

        # Compile PDF
        click.echo("\n🔨 Compiling PDF...")
        compiler = LaTeXCompiler()
        template_dir = Path("templates") / template
        success, message = compiler.compile(generated_tex, output_dir, template_dir)

        if success:
            click.secho(f"✓ {message}", fg="green")

            if preview:
                pdf_path = output_dir / f"resume_{timestamp}.pdf"
                click.echo(f"\n👀 Opening PDF: {pdf_path}")
                click.launch(str(pdf_path))

            click.echo("\n✅ Resume generation complete!")
        else:
            click.secho(f"✗ {message}", fg="red", err=True)
            click.echo("\n💡 Tip: Use --latex-only to generate just the .tex file")
            sys.exit(1)

    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file):
    """Validate resume data without generating files."""
    try:
        click.echo(f"📋 Validating {input_file}...")

        with open(input_file, "r") as f:
            data_dict = json.load(f)

        data = ResumeData(**data_dict)

        click.secho("\n✓ Data is valid!", fg="green")
        click.echo("\n📊 Summary:")
        click.echo(f"  Name: {data.contact.name}")
        click.echo(f"  Email: {data.contact.email}")
        click.echo(f"  Experience entries: {len(data.experience)}")
        click.echo(f"  Skill categories: {len(data.skills)}")
        click.echo(f"  Certifications: {len(data.certifications)}")
        click.echo(f"  Education entries: {len(data.education)}")

    except Exception as e:
        click.secho(f"\n✗ Validation failed: {str(e)}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def convert(input_file, output_file):
    """Convert resume data to LaTeX without compiling."""
    try:
        click.echo(f"📄 Loading resume data from {input_file}...")

        with open(input_file, "r") as f:
            data_dict = json.load(f)

        data = ResumeData(**data_dict)

        click.echo("📝 Generating LaTeX...")
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        generator = LaTeXGenerator("templates")
        generated = generator.generate(data, output_path)

        click.secho(f"✓ LaTeX file created: {generated}", fg="green")

    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg="red", err=True)
        sys.exit(1)


@cli.command()
def example():
    """Show example resume data structure."""
    example_data = {
        "contact": {
            "name": "Your Name",
            "email": "your.email@example.com",
            "phone": "+1 (555) 123-4567",
            "linkedin": "https://linkedin.com/in/yourprofile",
            "location": "City, State",
        },
        "summary": "Brief professional summary highlighting your expertise and experience (50-500 characters).",
        "experience": [
            {
                "company": "Company Name",
                "role": "Your Role",
                "location": "City, State",
                "start_date": "2020-01-01",
                "end_date": None,  # None for current position
                "achievements": [
                    "Achievement with metrics and impact",
                    "Another achievement demonstrating value",
                ],
            }
        ],
        "skills": {
            "Category 1": ["Skill 1", "Skill 2", "Skill 3"],
            "Category 2": ["Skill A", "Skill B"],
        },
        "certifications": [
            {
                "name": "Certification Name",
                "issuer": "Issuing Organization",
                "date": "2023-01-01",
            }
        ],
        "education": [
            {"degree": "Degree Name", "institution": "Institution Name", "year": 2020}
        ],
    }

    click.echo("📝 Example Resume Data Structure:\n")
    click.echo(json.dumps(example_data, indent=2))
    click.echo("\n💡 Save this to a JSON file and customize with your information")
    click.echo("💡 See examples/sample_data.json for a complete example")


if __name__ == "__main__":
    cli()
