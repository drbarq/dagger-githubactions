Prompt for Claude Code:
Create a proof-of-concept CI/CD pipeline that demonstrates using Doppler (secrets management), Dagger (CI/CD as code), and GitHub Actions together, with the ability to run the same pipeline both locally and in CI.
Requirements:

Simple Python Application

A minimal "Hello World" style Python app (no frontend needed)
Include at least one simple unit test
The app should use at least one secret from Doppler (e.g., an API key that gets printed/logged)


Dagger Pipeline (using Python SDK)

Create Dagger functions for:

Building the Python app (install dependencies, etc.)
Running tests
Publishing/outputting an artifact (whatever is simplest and free - could be GitHub Packages, or just creating a build artifact)


Integrate Doppler to fetch secrets and inject them into the Dagger pipeline
Ensure the same Dagger code works identically locally and in CI


GitHub Actions Workflow

Workflow file that:

Triggers on push/pull request
Sets up Dagger CLI
Authenticates with Doppler
Runs the Dagger pipeline functions


Should use the exact same Dagger commands that work locally


Documentation (README.md)

Prerequisites (Dagger CLI, Doppler CLI, Python)
How to set up Doppler (creating a project, adding a secret)
How to run the pipeline locally (step-by-step commands)
How the GitHub Actions workflow works
Environment variables/secrets needed in GitHub



Project Structure:

Keep it simple and well-organized
Include a .github/workflows/ directory for the GitHub Actions workflow
Include all necessary configuration files (requirements.txt, etc.)
No need for Docker Compose or other unnecessary complexity

Goal: A developer should be able to clone this repo, set up Doppler with one secret, run dagger call build and dagger call test locally, and see the same thing work automatically in GitHub Actions when they push.