FROM quay.io/jupyter/datascience-notebook:latest

# Switch to root user to install packages
USER root

# Install required system packages
RUN apt-get update && \
    apt-get install -y wget curl lsb-release rpm apt-transport-https && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/notebooks

# Copy requirements
COPY ./requirements.txt .

# Install dependencies
RUN pip install --upgrade --no-cache-dir -r ./requirements.txt

# Add a JupyterLab extension for version control if needed
RUN jupyter labextension install @jupyterlab/git
RUN python -m spacy download en_core_web_sm

# Switch back to the notebook user
USER ${NB_UID}

EXPOSE 8888

CMD jupyter lab --ip=* --port=8888 --no-browser --notebook-dir=/home/notebooks