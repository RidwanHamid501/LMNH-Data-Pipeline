# Deployment

### Overview

Deployment for this project is handled automatically through a GitHub Actions workflow. Each time code is pushed to the `main` branch, or a pull request is merged into `main`, the GitHub Actions workflow (`deployment.yml`) will run to ensure code quality and deployment to the EC2 instance.

### GitHub Actions Workflow

The deployment workflow consists of the following stages:
1. **Speak**: Outputs a simple message for confirmation.
2. **Test**: Runs unit tests using `pytest` to ensure code integrity.
3. **Lint**: Analyses code quality using `pylint`, enforcing a minimum quality threshold.
4. **Deploy**: Deploys code to the staging server (EC2 instance) once tests and linting pass.

### GitHub Secrets

The workflow relies on GitHub Secrets for sensitive data and configurations required during deployment. Below are the key secrets used in the workflow:

- **`SSH_PRIVATE_KEY`**: Private SSH key for secure access to the EC2 instance (`.pemkey` file).
- **`REMOTE_HOST`**: The hostname or IP address of the EC2 instance.
- **`REMOTE_USER`**: The user account on the EC2 instance with permissions for deployment (typically `ec2-user`).
- **`SOURCE`**: Defines the path in the repository that should be deployed, formatted as `./path`.
- **`TARGET`**: Specifies the path to the cloned repository in the EC2 instance where files should be deployed.

### Deployment Scripts

Additional scripts are included in this `deployment/` folder for setup and deployment:

- **`deployment.yml`**: GitHub Actions workflow for automated deployment. If you need to customise or rerun the workflow, you can paste the contents of this file directly into the GitHub Actions Workflow editor (`.github/workflows/deployment.yml`), and rerun it as needed.

