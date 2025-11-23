# LaTeX Resume Generator

LaTeX-based resume generator with a two-column layout for tech professionals.

> This tool is generated using LLMs out of a personal interest in possibilities and capabilities of AI-assisted software development. It is not affiliated with any employer or organization.

## Features

- Two-column design with sidebar
- JSON-driven content
- Docker-based compilation (no local LaTeX required)
- Type-safe validation
- Customizable styling
- 2-page optimization
- Profile photo support
- Privacy protection tools

## Setup

**Requirements:**
- Docker (recommended), or
- Python 3.8+ and LaTeX (TeX Live/MiKTeX/MacTeX)

**Using Docker:**

```bash
git clone https://github.com/YOUR_USERNAME/latex-resume-generator.git
cd latex-resume-generator

cp input/example_data.json input/my_resume.json
# Edit my_resume.json

python3 src/main.py generate input/my_resume.json --latex-only --output output
cp templates/awesome-cv-tech/awesome-cv.cls output/

docker-compose run --rm resume-builder bash -c \
  "cd /workspace/output && \
   pdflatex -interaction=nonstopmode resume_*.tex && \
   pdflatex -interaction=nonstopmode resume_*.tex"
```

Output: `output/resume_TIMESTAMP.pdf`

**Local installation:**

```bash
pip install -r requirements.txt
# Install LaTeX for your platform
python3 src/main.py generate input/my_resume.json --latex-only --output output
```

## Data Format

Resume data is stored in JSON:

```json
{
  "contact": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1 555 123 4567",
    "linkedin": "https://www.linkedin.com/in/johndoe/",
    "github": "https://github.com/johndoe",
    "location": "San Francisco, CA",
    "position_title": "Senior Software Engineer"
  },
  "summary": "Brief professional summary...",
  "experience": [
    {
      "company": "Tech Company",
      "role": "Senior Software Engineer",
      "location": "San Francisco, CA",
      "start_date": "2022-01-01",
      "end_date": null,
      "achievements": [
        "Led migration to cloud architecture, reducing costs by 40%",
        "Designed CI/CD pipelines improving deployment by 3x"
      ]
    }
  ],
  "skills": {
    "Cloud Platforms": ["AWS", "Azure", "GCP"],
    "Programming": ["Python", "Go", "Bash"]
  },
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2023 Jan"
    }
  ],
  "education": [
    {
      "degree": "B.Sc. Computer Science",
      "institution": "University Name",
      "year": 2018
    }
  ],
  "languages": [
    {"language": "English", "proficiency": "Native"}
  ],
  "interests": ["Open Source", "Cloud Architecture"]
}
```

See `input/example_data.json` for complete example.

## Customization

**Colors** - Edit `templates/awesome-cv-tech/awesome-cv.cls`:

```latex
\definecolor{primary}{HTML}{2596be}
\definecolor{text}{RGB}{44, 62, 80}
```

**Layout:**
- Page margins: Modify `geometry` package settings
- Sidebar width: Adjust `\columnratio`
- Spacing: Change `\vspace` values

**Profile photo:**

```bash
# Process photo backgrounds
python3 src/process_profile_photo.py

# Save as input/profile_photo.png
```

## Project Structure

```
.
├── input/              # Resume data (gitignored)
├── output/             # Generated PDFs (gitignored)
├── src/                # Python source
├── templates/          # LaTeX templates
├── tests/              # Test suite
├── docker-compose.yml
└── requirements.txt
```

## Testing

```bash
pip install pytest
pytest tests/
pytest tests/ --cov=src --cov-report=html
```

## Validation

Data is validated for:
- Email/phone format
- Valid URLs
- Logical dates
- Required fields
- Text length limits

## Tips

**Achievements:**
- Use metrics: "Reduced costs by 40%"
- Show impact: "Improved uptime to 99.99%"
- Include scale: "Processing 100K+ transactions/second"

**Skills:**
- Top 3 categories go in sidebar
- Group by logical categories
- 5-10 skills per category

**Length:**
- Target 2 pages
- Keep recent 4-5 positions
- 3-5 achievements per role

## Troubleshooting

**LaTeX errors:** Run pdflatex twice (resolves references)

**Exceeds 2 pages:**
- Remove older positions
- Shorten achievements
- Move skills to "Additional Skills"

**Docker fails:** Check resources (4GB+ recommended)

**Font issues:** Docker image includes required fonts

## Contributing

Fork, create feature branch, add tests, submit PR. See `CONTRIBUTING.md`.

## License

MIT License - see LICENSE file.

## Credits

Based on [Awesome-CV](https://github.com/posquit0/Awesome-CV) template.

---

**Note:** This is a generator tool, not a personal resume. Keep your data in `input/` (gitignored).

