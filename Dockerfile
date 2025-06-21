FROM python:3.10-slim

# Install Chromium and ChromeDriver
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for headless Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/lib/chromium/chromedriver

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ src/

ENTRYPOINT ["python", "src/scraper.py"]
CMD ["--help"]
