# Docker Compose Project Development Prompt Template
This document will guide you through the steps of working with LLMs to build a professional and secure Docker Compose Project. The goal is to help you jump start your project and you may need to add more steps and prompts. We hope you'll find this document useful and contribute your prompts to improve it.

## Step 1 - Construct Project Context
In this step, you will write the description of the variable **{{Context}}** with the following details.
- Goal: Clearly state the project’s objective. Explain why this project is important and what problem it aims to solve.
- The Key Components: Introduce the services used and why they were chosen, but focus on their role in achieving the project’s goal.
- Explain Service Interactions: Briefly describe how these components interact and how the architecture fits together.
- Target Audience & Usage: Mention the intended users or use cases, especially if it has beginner-friendly features or advanced customization for experienced users.

Here is an example:
```
Context = "The OllaLab Docker Compose project is designed to help both novice and experienced developers rapidly set up and begin working on LLM-based projects. This is achievable via simplified environment configuration and a cohesive set of tools for research and development. The project includes several key components. Ollama with LLMs. LangChain for orchestrating LLM pipelines, allowing users to seamlessly connect, manage, and optimize their workflows. Jupyter Lab serves as the integrated development environment (IDE), providing users with an interactive space to write, test, and iterate code efficiently. Neo4J vector database for managing retrieval-augmented generation (RAG) tasks, supporting advanced data storage and retrieval based on vector embeddings. Streamlit to create dynamic web applications, enabling developers to build and deploy user-friendly interfaces for their models and workflows."
```

## Step 2 - Identify Project Requirements
In this step, you will write the description of the variable **{{Requirements}}** that may involve some or all of the following details.
### Operation requirements
- Structure: project directory structure should follow best practices, docker-compose.yml must adhere to clean architecture principles
- Volumes: Indicate whether a specific component needs a volume.
- Linked volumes: Indicate whether certain components need to share a volume.
- Centralized Logging: indicate whether a logging servie is needed to centralize and analyze logs.
- Monitor Services: indicate whether a monitor service is needed to track container performance and security.
- Scaling Services: indicate wheter Docker Compose’s scaling feature is needed to scale services horizontally.
- Load Balancing: indicate whether a load balancer (e.g., HAProxy, Traefik) is needed to distribute traffic between service replicas.
- Automated Deployments: Indicate whether CI/CD tools like Jenkins or GitLab CI will be used to automate testing and deployment of Docker Compose services.
- Multi-Stage Images: Use multi-stage builds to optimize image size and reduce unnecessary dependencies.
- Optimize for Performance: Tune resource limits (cpu, memory) for each container for better performance in production.
### Security and test requirements
- Use Minimal Base Images: Opt for lightweight images (e.g., alpine) to reduce attack surface.
Restrict Service Privileges: Run containers with least privileges by using non-root users.
- Handle Secrets Securely: Store sensitive data (passwords, certificates) using Docker secrets or a secure vault system.
- Limit Container Capabilities: Use Docker Compose security options (e.g., cap_drop, read_only, no-new-privileges).
- Keep Images Up-to-Date: Use stable versions and regularly update images for security patches.
- Automated Tests: Include integration and unit tests for services, run within the Docker containers during the build process.
- Security Scans: Use tools like Clair or Trivy to scan Docker images for vulnerabilities.
### Networking and Firewalls
- Isolate Networks: Use Docker's network isolation to separate internal service traffic from external traffic.
- Expose Only Necessary Ports: Limit exposed ports to those necessary for external access.
- Configure Firewalls: Use host and container-level firewalls to restrict network access.

Here is an example:
```
Requirements = "The requirements for this project are: Project directory structure should follow best practices. The docker-compose.yml must adhere to clean architecture principles. Neo4j, streamlit, and jupyter lab instances must have volumes. The Jupyter Lab instance can modify/export streamlit python files to  the Streamlit instance application folder. The project should have Centralized Logging, Monitor Services, Load Balancing, Multi-Stage Images as needed. The project should use minimal Base Images, handle Secrets securely, limit container capabilities, keep images up to date, support automated tests, support security scans, isolate networks, expose only necessary ports, and use host and container-level firewalls to restrict network access."
```
## Step 3 - Generate Project Folders and Files
In this step, you will write a prompt to instruct the LLM to output the needed project folders and files. The template is as follows:

{{Context}}

{{Requirements}}

Please generate the needed folders and files. Please also make sure you are not missing any file and generate as specific as possible the content of each file.

For example:
```
The OllaLab Docker Compose project is designed to help both novice and experienced developers rapidly set up and begin working on LLM-based projects. This is achievable via simplified environment configuration and a cohesive set of tools for research and development. The project includes several key components. Ollama with LLMs. LangChain for orchestrating LLM pipelines, allowing users to seamlessly connect, manage, and optimize their workflows. Jupyter Lab serves as the integrated development environment (IDE), providing users with an interactive space to write, test, and iterate code efficiently. Neo4J vector database for managing retrieval-augmented generation (RAG) tasks, supporting advanced data storage and retrieval based on vector embeddings. Streamlit to create dynamic web applications, enabling developers to build and deploy user-friendly interfaces for their models and workflows.
The requirements for this project are: Project directory structure should follow best practices. The docker-compose.yml must adhere to clean architecture principles. Neo4j, streamlit, and jupyter lab instances must have volumes. The Jupyter Lab instance can modify/export streamlit python files to  the Streamlit instance application folder. The project should have Centralized Logging, Monitor Services, Load Balancing, Multi-Stage Images as needed. The project should use minimal Base Images, handle Secrets securely, limit container capabilities, keep images up to date, support automated tests, support security scans, isolate networks, expose only necessary ports, and use host and container-level firewalls to restrict network access.
Please generate the needed folders and files. Please also make sure you are not missing any file and generate as specific as possible the content of each file.
```

## Step 4 - Request Missing Files
In this step, you will write a prompt to ask the AI to double check its work and provide the contents of any missing files. The prompt is:
```
{{model's response in the previous step}}
Please double check your work and see if there is any file that you didn't give me, and generate as specific as possible the content of each file.
```

## Step 5 - Request Double-checking of Docker Compose File
In this step, you will write a prompt to ask the AI to double check the docker-compose.yml file and fix any potential error. The prompt is:
```
Check the following docker compose file and fix as needed.
{{the content of docker-compose.yml file}}
```

## Note:
While this template should allow the LLM to give you a really good start at building out your Docker Compose project, it is not perfect. You need to double check the results and make changes/improvments as needed. 