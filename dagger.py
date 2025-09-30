"""
Dagger pipeline for building, testing, and publishing the Python app.
This pipeline integrates Doppler secrets and works identically locally and in CI.
"""
import sys
import dagger
from dagger import dag, function, object_type


@object_type
class Nine:
    @function
    async def build(self) -> dagger.Container:
        """
        Build the application container with dependencies installed.
        """
        return (
            dag.container()
            .from_("python:3.11-slim")
            .with_directory("/app", dag.host().directory(".", exclude=[".git", "__pycache__", "*.pyc", ".pytest_cache"]))
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
        )

    @function
    async def test(self, secret_message: dagger.Secret) -> str:
        """
        Run tests with secrets injected directly as parameters.
        No Doppler CLI needed in container - secrets come from host via doppler run.

        Args:
            secret_message: The SECRET_MESSAGE from Doppler
        """
        # Get the built container
        container = await self.build()

        # Run tests with secrets injected as environment variables
        result = await (
            container
            .with_secret_variable("SECRET_MESSAGE", secret_message)
            .with_exec(["pytest", "-v"])
            .stdout()
        )

        return result

    @function
    async def publish(self, registry: str, username: str, password: dagger.Secret, tag: str = "latest") -> str:
        """
        Build and publish the container image to a registry.

        Args:
            registry: Container registry URL (e.g., "docker.io/username")
            username: Registry username
            password: Registry password as a Dagger secret
            tag: Image tag (default: "latest")
        """
        container = await self.build()

        # Set up the final runtime container
        runtime = (
            container
            .with_entrypoint(["python", "app.py"])
            .with_exposed_port(5000)
        )

        # Publish to registry
        image_ref = f"{registry}/nine-app:{tag}"
        address = await runtime.with_registry_auth(registry.split("/")[0], username, password).publish(image_ref)

        return f"Published to {address}"

    @function
    async def run_local(self, secret_message: dagger.Secret) -> dagger.Service:
        """
        Run the application locally with secrets injected directly.
        No Doppler CLI needed in container - secrets come from host via doppler run.

        Args:
            secret_message: The SECRET_MESSAGE from Doppler
        """
        container = await self.build()

        # Run with secrets injected as environment variables
        return (
            container
            .with_secret_variable("SECRET_MESSAGE", secret_message)
            .with_exposed_port(5000)
            .with_exec(["python", "app.py"])
            .as_service()
        )