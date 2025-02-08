FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Create a user for the container
# RUN groupadd -g 1001 devuser && useradd -ms /bin/bash -u 1001 -g 1001 devuser
# USER devuser

# Install the xz-utils package
RUN apt-get update && apt-get install -y curl=7.81.0-1ubuntu1.20

# Add HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost/ || exit 1
