# Base image with Python
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libglib2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Set working directory
WORKDIR /app

# Copy repo files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for headless Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV DISPLAY=:99

# Default command
CMD ["python", "cli.py", "--state", "Delhi", "--district", "New Delhi", "--complex", "Tis Hazari", "--all", "--date", "today"]
