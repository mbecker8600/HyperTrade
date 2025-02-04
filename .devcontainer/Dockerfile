FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Create a user for the container
RUN useradd -ms /bin/bash devuser

# Install the xz-utils package
RUN apt-get update && apt-get install -y curl

# Add HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost/ || exit 1