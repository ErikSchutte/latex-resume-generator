"""LaTeX compiler wrapper for generating PDF resumes."""

import subprocess
import re
import shutil
from pathlib import Path


class LaTeXCompiler:
    """Compile LaTeX files to PDF using pdflatex or xelatex."""

    def __init__(self, engine: str = "pdflatex", timeout: int = 30):
        """
        Initialize the compiler.

        Args:
            engine: LaTeX engine to use ('pdflatex' or 'xelatex')
            timeout: Maximum compilation time in seconds
        """
        self.engine = engine
        self.timeout = timeout

    def compile(
        self, tex_file: Path, output_dir: Path | None = None, template_dir: Path | None = None
    ) -> tuple[bool, str]:
        """
        Compile a LaTeX file to PDF.

        Args:
            tex_file: Path to the .tex file
            output_dir: Directory for output files (defaults to tex_file parent)
            template_dir: Directory containing template files to copy (e.g., .cls files)

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Convert to absolute path first
        tex_file = Path(tex_file).resolve()
        
        if not tex_file.exists():
            return False, f"TeX file not found: {tex_file}"

        if output_dir is None:
            output_dir = tex_file.parent
        else:
            output_dir = Path(output_dir).resolve()

        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy template files if template_dir provided
        if template_dir:
            template_dir = Path(template_dir).resolve()
            if template_dir.exists():
                for cls_file in template_dir.glob("*.cls"):
                    shutil.copy2(cls_file, output_dir / cls_file.name)
                # Also copy config directory if exists
                config_dir = template_dir / "config"
                if config_dir.exists():
                    output_config_dir = output_dir / "config"
                    if output_config_dir.exists():
                        shutil.rmtree(output_config_dir)
                    shutil.copytree(config_dir, output_config_dir)
        
        # Copy profile photo if exists in input directory
        input_photo = Path("input/profile_photo_final.png")
        if input_photo.exists():
            shutil.copy2(input_photo, output_dir / input_photo.name)

        # Compile twice to resolve references
        for pass_num in range(2):
            cmd = [
                self.engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_dir}",
                str(tex_file),
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=output_dir,
                )

                if result.returncode != 0:
                    error_msg = self._parse_errors(result.stdout)
                    return (
                        False,
                        f"Compilation failed (pass {pass_num + 1}/2): {error_msg}",
                    )

            except subprocess.TimeoutExpired:
                return False, f"Compilation timeout after {self.timeout}s"
            except FileNotFoundError:
                return (
                    False,
                    f"LaTeX engine '{self.engine}' not found. Please install TeX Live or use Docker.",
                )
            except Exception as e:
                return False, f"Compilation error: {str(e)}"

        # Verify PDF was created
        pdf_file = output_dir / tex_file.with_suffix(".pdf").name
        if not pdf_file.exists():
            return False, "PDF file was not generated"

        # Validate PDF
        valid, msg = self._validate_pdf(pdf_file)
        if not valid:
            return False, msg

        # Cleanup auxiliary files
        self._cleanup(output_dir, tex_file.stem)

        return True, f"Successfully generated {pdf_file}"

    def _parse_errors(self, log: str) -> str:
        """
        Extract meaningful error messages from LaTeX log output.

        Args:
            log: LaTeX compilation log

        Returns:
            Human-readable error message
        """
        # Look for ! Error lines
        errors = re.findall(r"! (.+)", log)
        if errors:
            return errors[0]

        # Look for undefined control sequences
        undefined = re.findall(
            r"Undefined control sequence.*?\n.*?(\\.+)", log, re.DOTALL
        )
        if undefined:
            return f"Undefined command: {undefined[0].strip()}"

        # Look for missing files
        missing = re.findall(r"File `(.+?)\' not found", log)
        if missing:
            return f"Missing file: {missing[0]}"

        return "Unknown compilation error. Check the .log file for details."

    def _validate_pdf(self, pdf_file: Path) -> tuple[bool, str]:
        """
        Validate the generated PDF file.

        Args:
            pdf_file: Path to PDF file

        Returns:
            Tuple of (valid: bool, message: str)
        """
        try:
            # Check file size
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            if size_mb > 5:
                return False, f"PDF too large: {size_mb:.2f}MB (max 5MB)"

            if size_mb < 0.001:  # Less than 1KB
                return False, "PDF file is too small, likely corrupted"

            # Try to check page count using pdfinfo if available
            try:
                result = subprocess.run(
                    ["pdfinfo", str(pdf_file)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    pages_match = re.search(r"Pages:\s+(\d+)", result.stdout)
                    if pages_match:
                        pages = int(pages_match.group(1))
                        if pages > 2:
                            return (
                                False,
                                f"Resume exceeds 2 pages ({pages} pages). Consider condensing content.",
                            )
            except FileNotFoundError:
                # pdfinfo not available, skip page count check
                pass

            return True, "PDF validated successfully"

        except Exception as e:
            return False, f"PDF validation error: {str(e)}"

    def _cleanup(self, output_dir: Path, basename: str) -> None:
        """
        Remove auxiliary LaTeX files.

        Args:
            output_dir: Directory containing auxiliary files
            basename: Base name of the .tex file (without extension)
        """
        extensions = [
            ".aux",
            ".log",
            ".out",
            ".toc",
            ".fls",
            ".fdb_latexmk",
            ".synctex.gz",
        ]

        for ext in extensions:
            aux_file = output_dir / f"{basename}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
