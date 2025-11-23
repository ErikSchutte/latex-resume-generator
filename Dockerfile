FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install TeX Live and dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-xetex \
    latexmk \
    python3 \
    python3-pip \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash resumeuser && \
    mkdir -p /workspace && \
    chown -R resumeuser:resumeuser /workspace

WORKDIR /workspace

# Install Python dependencies as root
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER resumeuser

# Copy project files
COPY --chown=resumeuser:resumeuser . .

CMD ["python3", "src/main.py"]
