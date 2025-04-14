# Use the official Python image as a base
FROM python:3.12

# Install uv
RUN pip install uv

# Create a non-root user and set permissions
RUN useradd -ms /bin/bash vscode \
    && chown -R vscode:vscode /home/vscode

# Set the default user
USER vscode

# Set the working directory
WORKDIR /workspace

