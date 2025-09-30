"""
Dagger pipeline for building, testing, and publishing the Python app.
This pipeline integrates Doppler secrets and works identically locally and in CI.
"""
import dagger
from dagger import dag, function, object_type


@object_type
class Nine:
    @function
    def build(self) -> dagger.Container:
        """
        Build the application container with dependencies installed.
        """
        # Get files from .dagger directory
        source = dag.current_module().source().directory(".")

        return (
            dag.container()
            .from_("python:3.11-slim")
            .with_workdir("/app")
            .with_directory(".", source, include=["requirements.txt", "app.py", "test_app.py"])
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
            .with_exposed_port(5001)
        )

        # Publish to registry
        image_ref = f"{registry}/nine-app:{tag}"
        address = await runtime.with_registry_auth(registry.split("/")[0], username, password).publish(image_ref)

        return f"Published to {address}"

    @function
    async def run_local(self, secret_message: dagger.Secret) -> dagger.Service:
        """
        Run the application as a service (for container-to-container communication).

        To access from localhost, use: dagger call serve --secret-message=env:SECRET_MESSAGE

        Args:
            secret_message: The SECRET_MESSAGE from Doppler
        """
        container = await self.build()

        # Run with secrets injected as environment variables
        return (
            container
            .with_secret_variable("SECRET_MESSAGE", secret_message)
            .with_exposed_port(5001)
            .with_exec(["python", "app.py"])
            .as_service()
        )

    @function
    async def export_image(self, tag: str = "nine-app:latest") -> str:
        """
        Export the container image to your local Docker daemon.

        Usage:
          dagger call export-image --tag nine-app:latest

        Then run with Docker and Doppler:
          doppler run -- docker run -p 5000:5000 -e SECRET_MESSAGE=$SECRET_MESSAGE nine-app:latest

        Args:
            tag: Docker image tag (default: nine-app:latest)
        """
        container = await self.build()

        # Export to local Docker daemon
        await container.export(tag)

        return f"""
Image exported as: {tag}

To run locally with Doppler:
  doppler run -- docker run -p 5001:5001 -e SECRET_MESSAGE=\$SECRET_MESSAGE {tag}

Then visit: http://localhost:5001
        """.strip()
