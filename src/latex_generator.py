"""
LaTeX Resume Generator
Generates a professional LaTeX resume from YAML data using the moderncv template.
"""

import yaml
import sys
from pathlib import Path
from typing import Any
from datetime import datetime


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text."""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def format_date(date_str: str | None) -> str:
    """Format date string for display."""
    if not date_str:
        return ""
    if date_str.lower() == "present":
        return "Present"
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m")
        return date_obj.strftime("%b %Y")
    except ValueError:
        return date_str


def generate_header(data: dict[str, Any]) -> str:
    """Generate the LaTeX header section."""
    personal = data.get('personal_info', {})
    
    name = escape_latex(personal.get('name', ''))
    title = escape_latex(personal.get('title', ''))
    
    header = [
        r"\documentclass[11pt,a4paper,sans]{moderncv}",
        r"\moderncvstyle{banking}",
        r"\moderncvcolor{blue}",
        r"\usepackage[scale=0.85]{geometry}",
        r"\usepackage{hyperref}",
        r"\usepackage{fontawesome5}",
        "",
        f"\\name{{{name.split()[0] if name else ''}}}{{{' '.join(name.split()[1:]) if name else ''}}}",
        f"\\title{{{title}}}",
    ]
    
    # Add contact information
    if personal.get('phone'):
        header.append(f"\\phone[mobile]{{{escape_latex(personal['phone'])}}}")
    if personal.get('email'):
        header.append(f"\\email{{{escape_latex(personal['email'])}}}")
    if personal.get('linkedin'):
        header.append(f"\\social[linkedin]{{{escape_latex(personal['linkedin'])}}}")
    if personal.get('github'):
        header.append(f"\\social[github]{{{escape_latex(personal['github'])}}}")
    if personal.get('website'):
        header.append(f"\\homepage{{{escape_latex(personal['website'])}}}")
    if personal.get('location'):
        header.append(f"\\address{{{escape_latex(personal['location'])}}}{{}}{{}}")
    
    header.extend([
        "",
        r"\begin{document}",
        r"\makecvtitle",
        ""
    ])
    
    return "\n".join(header)


def generate_summary(data: dict[str, Any]) -> str:
    """Generate the professional summary section."""
    summary = data.get('summary', '').strip()
    if not summary:
        return ""
    
    return f"""\\section{{Professional Summary}}
{escape_latex(summary)}

"""


def generate_experience(data: dict[str, Any]) -> str:
    """Generate the experience section."""
    experiences = data.get('experience', [])
    if not experiences:
        return ""
    
    section = ["\\section{Professional Experience}\n"]
    
    for exp in experiences:
        company = escape_latex(exp.get('company', ''))
        position = escape_latex(exp.get('position', ''))
        location = escape_latex(exp.get('location', ''))
        start = format_date(exp.get('start_date'))
        end = format_date(exp.get('end_date'))
        
        section.append(f"\\cventry{{{start} -- {end}}}{{{position}}}{{{company}}}{{{location}}}{{}}{{")
        
        achievements = exp.get('achievements', [])
        if achievements:
            section.append("\\begin{itemize}")
            for achievement in achievements:
                section.append(f"  \\item {escape_latex(achievement)}")
            section.append("\\end{itemize}")
        
        section.append("}\n")
    
    return "\n".join(section)


def generate_education(data: dict[str, Any]) -> str:
    """Generate the education section."""
    education = data.get('education', [])
    if not education:
        return ""
    
    section = ["\\section{Education}\n"]
    
    for edu in education:
        degree = escape_latex(edu.get('degree', ''))
        institution = escape_latex(edu.get('institution', ''))
        location = escape_latex(edu.get('location', ''))
        grad_date = format_date(edu.get('graduation_date'))
        gpa = edu.get('gpa', '')
        
        extra = f"GPA: {gpa}" if gpa else ""
        
        section.append(f"\\cventry{{{grad_date}}}{{{degree}}}{{{institution}}}{{{location}}}{{{extra}}}{{")
        
        honors = edu.get('honors', [])
        if honors:
            section.append("\\begin{itemize}")
            for honor in honors:
                section.append(f"  \\item {escape_latex(honor)}")
            section.append("\\end{itemize}")
        
        section.append("}\n")
    
    return "\n".join(section)


def generate_certifications(data: dict[str, Any]) -> str:
    """Generate the certifications section."""
    certs = data.get('certifications', [])
    if not certs:
        return ""
    
    section = ["\\section{Certifications}\n"]
    
    for cert in certs:
        name = escape_latex(cert.get('name', ''))
        issuer = escape_latex(cert.get('issuer', ''))
        date = format_date(cert.get('date'))
        credential = cert.get('credential_id', '')
        
        extra = f"ID: {escape_latex(credential)}" if credential else ""
        section.append(f"\\cventry{{{date}}}{{{name}}}{{{issuer}}}{{}}{{}}{{}}".replace('}{}}{}', f'}}{{{extra}}}{{}}'))
    
    section.append("")
    return "\n".join(section)


def generate_skills(data: dict[str, Any]) -> str:
    """Generate the skills section."""
    skills = data.get('skills', [])
    if not skills:
        return ""
    
    section = ["\\section{Technical Skills}\n"]
    
    for skill_cat in skills:
        category = escape_latex(skill_cat.get('category', ''))
        items = skill_cat.get('items', [])
        
        if items:
            items_str = ", ".join([escape_latex(item) for item in items])
            section.append(f"\\cvitem{{{category}}}{{{items_str}}}")
    
    section.append("")
    return "\n".join(section)


def generate_projects(data: dict[str, Any]) -> str:
    """Generate the projects section."""
    projects = data.get('projects', [])
    if not projects:
        return ""
    
    section = ["\\section{Notable Projects}\n"]
    
    for proj in projects:
        name = escape_latex(proj.get('name', ''))
        description = escape_latex(proj.get('description', ''))
        technologies = proj.get('technologies', [])
        
        tech_str = ", ".join([escape_latex(t) for t in technologies])
        
        section.append(f"\\cvitem{{{name}}}{{{description}}}")
        if tech_str:
            section.append(f"\\cvitem{{}}{{\\textit{{Technologies:}} {tech_str}}}")
        
        achievements = proj.get('achievements', [])
        if achievements:
            section.append("\\begin{itemize}")
            for achievement in achievements:
                section.append(f"  \\item {escape_latex(achievement)}")
            section.append("\\end{itemize}")
    
    section.append("")
    return "\n".join(section)


def generate_publications(data: dict[str, Any]) -> str:
    """Generate the publications section."""
    pubs = data.get('publications', [])
    if not pubs:
        return ""
    
    section = ["\\section{Publications}\n"]
    
    for pub in pubs:
        title = escape_latex(pub.get('title', ''))
        publication = escape_latex(pub.get('publication', ''))
        date = format_date(pub.get('date'))
        
        section.append(f"\\cventry{{{date}}}{{{title}}}{{{publication}}}{{}}{{}}{{}}".replace('}{}}{}', '}}{}}}'))
    
    section.append("")
    return "\n".join(section)


def generate_languages(data: dict[str, Any]) -> str:
    """Generate the languages section."""
    languages = data.get('languages', [])
    if not languages:
        return ""
    
    section = ["\\section{Languages}\n"]
    
    for lang in languages:
        language = escape_latex(lang.get('language', ''))
        proficiency = escape_latex(lang.get('proficiency', ''))
        section.append(f"\\cvitem{{{language}}}{{{proficiency}}}")
    
    section.append("")
    return "\n".join(section)


def generate_latex_cv(data: dict[str, Any]) -> str:
    """Generate complete LaTeX CV document."""
    sections = [
        generate_header(data),
        generate_summary(data),
        generate_experience(data),
        generate_education(data),
        generate_certifications(data),
        generate_skills(data),
        generate_projects(data),
        generate_publications(data),
        generate_languages(data),
    ]
    
    sections.append("\\end{document}")
    
    return "\n".join(sections)


def main():
    """Main entry point for the LaTeX generator."""
    if len(sys.argv) != 3:
        print("Usage: python latex_generator.py <input_yaml> <output_tex>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Load YAML data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Generate LaTeX
    latex_content = generate_latex_cv(data)
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"LaTeX CV generated successfully: {output_file}")


if __name__ == "__main__":
    main()
