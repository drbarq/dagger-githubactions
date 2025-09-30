# Nine - Dagger + Doppler CI/CD Proof of Concept

A proof-of-concept demonstrating a CI/CD pipeline using Dagger for reproducible builds and Doppler for secrets management. The same Dagger pipeline code runs identically in local development and GitHub Actions.

## Overview

This project demonstrates:
- A simple Python Flask app that uses secrets from Doppler
- Dagger pipeline functions (build, test, publish) that work locally and in CI
- GitHub Actions workflow using the same Dagger commands
- Secrets managed through Doppler in both environments

## Architecture

```mermaid
flowchart TB
    subgraph Doppler["Doppler (Secrets Management)"]
        DopplerSecrets[("SECRET_MESSAGE<br/>+ Other Secrets")]
    end

    subgraph Local["Local Development"]
        DopplerCLI["Doppler CLI<br/>(doppler run)"]
        DaggerLocal["Dagger Pipeline<br/>(build, test)"]
        FlaskLocal["Flask App<br/>(port 5001)"]

        DopplerCLI -->|injects secrets<br/>as env vars| DaggerLocal
        DopplerCLI -->|injects secrets<br/>as env vars| FlaskLocal
    end

    subgraph GitHub["GitHub Actions (CI/CD)"]
        GHSecrets["GitHub Secrets<br/>(auto-synced)"]
        GHWorkflow["CI Workflow<br/>(.github/workflows/ci.yml)"]
        DaggerCI["Dagger Pipeline<br/>(same code!)"]

        GHSecrets -->|provides secrets<br/>as env vars| GHWorkflow
        GHWorkflow -->|runs| DaggerCI
    end

    subgraph Pipeline["Dagger Module (.dagger/src/nine/main.py)"]
        Build["@function build()"]
        Test["@function test()"]
        Publish["@function publish()"]

        Build --> Test
        Test --> Publish
    end

    DopplerSecrets -->|doppler login<br/>doppler setup| DopplerCLI
    DopplerSecrets -->|GitHub Integration<br/>(automatic sync)| GHSecrets

    DaggerLocal -.->|uses same code| Pipeline
    DaggerCI -.->|uses same code| Pipeline

    style Doppler fill:#4a90e2
    style Local fill:#90ee90
    style GitHub fill:#ffa07a
    style Pipeline fill:#dda0dd
```

**Key Points:**
- **One Pipeline, Two Environments**: The same Dagger code runs locally and in CI
- **Doppler Integration**: Local uses CLI, CI uses GitHub Actions integration (automatic sync)
- **No Secrets in Code**: All secrets flow from Doppler → Environment Variables → Dagger
- **Identical Commands**: `dagger call test` works the same everywhere

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

2. **Set up Python virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate it
   source venv/bin/activate

   # Install all dependencies (including dagger-io)
   pip install -r requirements.txt
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

For local development, run the Flask app directly with Doppler:

```bash
doppler run -- python app.py
```

Then visit `http://localhost:5001` in your browser.

The response will show:
```json
{
  "message": "Hello, World!",
  "secret": "your-secret-from-doppler"
}
```

Press `Ctrl+C` to stop the app.

**Note:** This runs the app directly on your machine (not in a Dagger container). The Dagger pipeline is used for build/test/publish in CI/CD, demonstrated by the `build` and `test` commands above.

## GitHub Actions Setup

### Option 1: Doppler GitHub Integration (Recommended)

Doppler has a native GitHub Actions integration that automatically syncs secrets without manual token management.

1. **Set up Doppler GitHub Integration**
   - In Doppler dashboard, go to your project → Integrations
   - Add a new "GitHub Actions" integration
   - Connect your GitHub repository
   - Select which config (dev/staging/prod) to sync
   - Doppler will create a `DOPPLER_TOKEN` secret in your GitHub repository automatically

2. **Add additional GitHub Secrets** (if needed for publishing)
   - Go to your repository settings → Secrets and variables → Actions
   - Add:
     - `REGISTRY_USERNAME` - Container registry username (optional)
     - `REGISTRY_PASSWORD` - Container registry password (optional)
     - `REGISTRY` - Container registry URL (optional, defaults to docker.io/username)

3. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Dagger + Doppler CI/CD pipeline"
   git push origin main
   ```

4. **View the workflow**
   - Go to the Actions tab in your GitHub repository
   - The workflow will run automatically on push and pull requests
   - The same `dagger call` commands run in CI as you use locally

### Option 2: Manual Service Token

If you prefer not to use the integration:

1. Generate a Doppler service token in your project settings
2. Add it as `DOPPLER_TOKEN` in GitHub Actions secrets manually
3. Continue with steps 2-4 above

## Project Structure

```
nine/
├── app.py                      # Simple Flask app that uses Doppler secrets
├── test_app.py                 # Unit tests for the app
├── requirements.txt            # Python dependencies
├── .dagger/                    # Dagger module directory
│   ├── app.py                  # Copy of app for Dagger (synced)
│   ├── test_app.py             # Copy of tests for Dagger (synced)
│   ├── requirements.txt        # Copy of requirements for Dagger (synced)
│   └── src/
│       └── nine/
│           └── main.py         # Dagger pipeline functions (build, test, publish)
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions workflow using Dagger
└── README.md                   # This file
```

**Note:** The application files (app.py, test_app.py, requirements.txt) are copied into `.dagger/` so the Dagger pipeline can access them. When you modify these files, remember to copy them to `.dagger/` as well.

## Key Features

### 🔄 Same Code Everywhere
The Dagger pipeline code in `.dagger/src/nine/main.py` runs identically:
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