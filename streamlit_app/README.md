<img src="https://github.com/GSA/fedramp-automation/raw/master/assets/FedRAMP_LOGO.png" alt="FedRAMP" width="76" height="94"><br />

# OllaLab-Lean - Interactive Web Apps

<h4>Interactive Web Apps for Local LLM-based Research and Development</h4>

[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)]()
[![python](https://img.shields.io/badge/python-3.11-green)]()
[![Static Badge](https://img.shields.io/badge/release-0.1-green?style=flat&color=green)]()
![GitHub License](https://img.shields.io/github/license/GSA/FedRAMP-OllaLab-Lean)

OllaLab-Lean - Interactive Web Apps are interactive web applications designed to help both novice and experienced developers with Research and Development tasks. The shared common components of the applications are:
- Python and related packages found in the requirement files.
- Ollama for managing local openweight Large Language Models (LLMs).
- LangChain for orchestrating LLM pipelines, allowing users to seamlessly connect, manage, and optimize their workflows.
- Streamlit server to locally host dynamic LLM-based web applications.
- Neo4J vector database supporting retrieval-augmented generation (RAG) tasks.

 &nbsp;

## Latest News
* [2024/10/30] 🚀 "OllaLab-Lean - Interactive Web Apps" section is officially initialized.

## Installation
OllaLab-Lean - Interactive Web Apps will be automatically installed following the main [OllaLab-Lean Installation](https://github.com/GSA/FedRAMP-OllaLab-Lean/tree/main#installation)

If you have issues with the main installation or simply want to install just the OllaLab-Lean - Interactive Web Apps, you can follow the steps below.

### Install Python
There are several ways to install Python. You may find the official guide in [Official Python Downloads](https://www.python.org/downloads/).

If you have Visual Studio Code installed, you may also follow [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)

### Install Python Virtual Environment
A virtual environment is created on top of an existing Python installation, known as the virtual environment’s “base” Python, and may optionally be isolated from the packages in the base environment, so only those explicitly installed in the virtual environment are available. More details are in [Creation of virtual environment](https://docs.python.org/3/library/venv.html)

Virtual environments are created by executing the venv module:
```
python -m venv /path/to/new/virtual/environment
```
If successfuly, a folder ".venv" will be created in /path/to/new/virtual/environment. You will then need to invoke the virtual environment. Assuming you are at the folder containing the ".venv" folder for the virtual environment you've just set up. You can launch the virtual environment by:
- On windows
```
 .venv/Scripts/activate.bat //In CMD
 .venv/Scripts/Activate.ps1 //In Powershel
```
- On Linux or Mac
```
source .venv/bin/activate
```

### Install Python Packages including Streamlit
In this step, you need to get to the folder containing the OllaLab-Lean - Interactive Web Apps where you can see this README file, the requirements.txt file, and the "app" folder. 

First, you need to update pip which is a package manager program included in your Python installation.
```
python3 -m pip install --upgrade pip
python3 -m pip --version
```

Then, you install the packages listed in the requirements.txt file.
```
python3 -m pip install -r requirements.txt
```

>[!NOTE]
>Some packages were disabled in the requirements.txt because they may cause the process to stop.
>You may install those packages individually later. You may also disable additional packages that you may not need.
>Individual packages can be installed by "pip install <package name>"

Feel free to check out [Additional info on installing packages within Python Virtual Environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)

### Install Ollama
Ollama is an AI tool that allows users to run large language models (LLMs) locally on their computer.
Installation files of Ollama for Mac, Linux, and Windows can be found at [Official Ollama Installation Files](https://ollama.com/download)

On Mac, you can also use "brew install ollama" to install Ollama on Homebrew.

To verify your Ollama installation, you may go to localhost:11434 or 127.0.0.1:11434. If the installation went well, you should see "Ollama is running".

Next, you need to pull LLMs from [Ollama Library](https://ollama.com/library). Your network may block the downloading. In such case, you may need to prepare the models locally which is a big topic by itself and will be supported by another documentation. Pull model is easy
```
ollama pull <model name>:[tag]
```
For example
```
ollama pull llama3.1:8b
ollama pull codellama:13b
```

> [!IMPORTANT]
> Check the model size in Ollama Library before you pull and use a model. The size of a model should not exceeed 75% of your available ram.

Use the following command to check whether the model(s) was pulled successfully
```
ollama list
```

### Install Neo4J
Neo4j is a graph database management system that stores and retrieves connected data including vectorized data for Retrieval Augmented Generation feature. The [Official Neo4J Installation Guide](https://neo4j.com/docs/operations-manual/current/installation/) contains the steps needed to install Neo4J on Linux, Mac, and Windows.

On Mac, you can also install Neo4J from Homebrew using "brew install neo4j"

Once Neo4J was installed and started, you should be able to view http://127.0.0.1:7474/browser/

You may then follow [Neo4J Create, Start, and Stop Databases](https://neo4j.com/docs/operations-manual/current/database-administration/standard-databases/create-databases/) to create your first database. 

## Video Tutorials
tba

## Planned Features and Applications
tba

## Contributing

We welcome contributions to OllaLab-Lean especially on the [Planned Features and Applications](#planned-features-and-applications)! 

Please see our [Contributing Guide](https://github.com/GSA/FedRAMP-OllaLab-Lean/blob/main/CONTRIBUTING.md) for more information on how to get started.

## License

[CC0 1.0 Universal](https://github.com/GSA/FedRAMP-OllaLab-Lean/blob/main/LICENSE)

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](https://github.com/GSA/FedRAMP-OllaLab-Lean/blob/main/CODE_OF_CONDUCT.md). By participating in this project and/or cloning the project, you agree to abide by its terms.
