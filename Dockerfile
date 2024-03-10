FROM debian:latest 

# Install X server and Firefox
RUN apt-get update && apt-get install -y \
    xvfb \
    firefox-esr \
    python3 \
    python3-pip \
    python3-venv \
    wget

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Install Python packages in the virtual environment
RUN /opt/venv/bin/pip install argparse requests selenium bs4


# Set up X server
RUN apt-get install -y xorg xserver-xorg-video-dummy

# Install geckodriver
RUN apt-get install -y wget && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    rm /tmp/geckodriver.tar.gz

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

ARG LINK

ENV DISPLAY=:99

# Move all files from current directory (excluding those specified in .dockerignore)
COPY . /app

# Start X server and Firefox
CMD Xvfb :99 -screen 0 1024x768x16
