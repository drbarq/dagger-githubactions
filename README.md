# Nine - Dagger + Doppler CI/CD Proof of Concept

A proof-of-concept demonstrating a CI/CD pipeline using Dagger for reproducible builds and Doppler for secrets management. The same Dagger pipeline code runs identically in local development and GitHub Actions.

## Overview

This project demonstrates:
- A simple Python Flask app that uses secrets from Doppler
- Dagger pipeline functions (build, test, publish) that work locally and in CI
- GitHub Actions workflow using the same Dagger commands
- Secrets managed through Doppler in both environments

## Prerequisites

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Dagger CLI**
   ```bash
   # Install Dagger
   cd /usr/local && curl -L https://dl.dagger.io/dagger/install.sh | sh

   # Verify installation
   dagger version
   ```

3. **Doppler CLI** (for local development)
   ```bash
   # macOS
   brew install dopplerhq/cli/doppler

   # Linux
   curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/install.sh' | sh

   # Verify installation
   doppler --version
   ```

4. **Doppler Account & Setup**
   - Create a free account at [doppler.com](https://doppler.com)
   - Create a new project called "nine"
   - Add a secret called `SECRET_MESSAGE` with any value (e.g., "Hello from Doppler!")
   - For CI/CD: Generate a service token for GitHub Actions

5. **Docker** (required by Dagger)
   - Dagger uses Docker to run containers
   - Install from [docker.com](https://www.docker.com/products/docker-desktop)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd nine
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   pip install dagger-io
   ```

3. **Authenticate with Doppler**
   ```bash
   # Login to Doppler (one-time setup)
   doppler login

   # Set up the project and config
   doppler setup
   ```

   Select your project (e.g., "nine") and config (e.g., "dev") when prompted.

## Running Locally with Dagger

All Dagger commands use the same pipeline code that runs in CI. **No need to copy/paste secrets** - Doppler CLI securely injects them!

### Build the application
```bash
dagger call build
```

### Run tests (with Doppler secrets)
```bash
doppler run -- dagger call test --secret-message=env:SECRET_MESSAGE
```

This runs tests with `SECRET_MESSAGE` injected from Doppler. The secret never touches disk!

### Run the app locally (with Doppler secrets)
```bash
doppler run -- dagger call run-local --secret-message=env:SECRET_MESSAGE up
```

Then visit `http://localhost:5000` to see the app with secrets loaded from Doppler.

### Publish to a container registry
```bash
dagger call publish \
  --registry="docker.io/yourusername" \
  --username="yourusername" \
  --password=env:REGISTRY_PASSWORD \
  --tag="latest"
```

## GitHub Actions Setup

1. **Add GitHub Secrets**

   Go to your repository settings → Secrets and variables → Actions, and add:

   - `DOPPLER_TOKEN` - Your Doppler service token
   - `REGISTRY_USERNAME` - Container registry username (optional, for publishing)
   - `REGISTRY_PASSWORD` - Container registry password (optional, for publishing)
   - `REGISTRY` - Container registry URL (optional, defaults to docker.io/username)

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Dagger + Doppler CI/CD pipeline"
   git push origin main
   ```

3. **View the workflow**
   - Go to the Actions tab in your GitHub repository
   - The workflow will run automatically on push and pull requests
   - The same `dagger call` commands run in CI as you use locally

## Project Structure

```
nine/
├── app.py                 # Simple Flask app that uses Doppler secrets
├── test_app.py           # Unit tests for the app
├── requirements.txt      # Python dependencies
├── dagger.py            # Dagger pipeline functions (build, test, publish)
├── pyproject.toml       # Project configuration for Dagger
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions workflow using Dagger
└── README.md            # This file
```

## Key Features

### 🔄 Same Code Everywhere
The Dagger pipeline code in `dagger.py` runs identically:
- On your laptop
- In CI (GitHub Actions)
- On any team member's machine

### 🔐 Secrets via Doppler
Secrets are managed centrally in Doppler:
- **Locally**: Use `doppler run` - no copy/pasting or storing secrets on disk
- **In CI**: Service tokens injected via GitHub Secrets
- Secrets passed as individual Dagger parameters for full control
- Zero secrets in code or config files

### 🧪 Testable Pipeline
The Dagger pipeline is itself written in Python and can be versioned, tested, and collaborated on like application code.

### 📦 Container Native
Everything runs in containers via Dagger, ensuring consistency across all environments.

## Doppler Configuration

In your Doppler project, you need at minimum:

- **SECRET_MESSAGE**: A test secret that the app will display

You can add more secrets as needed - they'll automatically be available to the app via environment variables.

## Troubleshooting

### "Not logged in to Doppler"
Run `doppler login` and authenticate with your browser.

### "Project not configured"
Run `doppler setup` in the project directory and select your project/config.

### Dagger connection issues
Ensure Docker is running:
```bash
docker ps
```

### Tests failing locally
First test without Dagger to isolate issues:
```bash
SECRET_MESSAGE="test" pytest -v
```

## Next Steps

This is a proof of concept. To productionize:

1. Add more comprehensive tests
2. Set up staging and production Doppler environments
3. Add deployment functions to Dagger pipeline
4. Implement blue/green or canary deployments
5. Add monitoring and alerting
6. Set up branch-specific workflows

## Resources

- [Dagger Documentation](https://docs.dagger.io)
- [Doppler Documentation](https://docs.doppler.com)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)