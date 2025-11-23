"""Utility functions for data validation and LaTeX processing."""

import re
from datetime import date


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in text.

    Args:
        text: The text to escape

    Returns:
        Text with LaTeX special characters properly escaped
    """
    # Define character replacements
    replacements = {
        "\\": r"\textbackslash ",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde ",
        "^": r"\textasciicircum ",
    }
    
    # Use regex to replace all at once to avoid cascading replacements
    pattern = re.compile("|".join(re.escape(key) for key in replacements.keys()))
    return pattern.sub(lambda m: replacements[m.group(0)], text)


def validate_date_range(start: date, end: date | None) -> bool:
    """
    Validate that a date range is logical.

    Args:
        start: Start date
        end: End date (None for ongoing/current)

    Returns:
        True if the date range is valid, False otherwise
    """
    if end is None:  # Current position
        return start <= date.today()

    return start < end <= date.today()


def format_date(d: date | None) -> str:
    """
    Format date for resume display.

    Args:
        d: Date to format (None for current/present)

    Returns:
        Formatted date string (e.g., "Jan 2020" or "Present")
    """
    if d is None:
        return "Present"

    return d.strftime("%b %Y")


def format_date_range(start: date, end: date | None) -> str:
    """
    Format a date range for resume display.

    Args:
        start: Start date
        end: End date (None for current/present)

    Returns:
        Formatted date range (e.g., "Jan 2020 -- Present")
    """
    start_str = format_date(start)
    end_str = format_date(end)
    return f"{start_str} -- {end_str}"


def validate_url(url: str) -> bool:
    """
    Basic URL validation.

    Args:
        url: URL to validate

    Returns:
        True if URL appears valid, False otherwise
    """
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding suffix if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    return filename
