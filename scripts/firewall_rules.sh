#!/bin/bash

# Allow only necessary incoming connections
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow specific ports
sudo ufw allow 7474    # Neo4j HTTP
sudo ufw allow 7687    # Neo4j Bolt
sudo ufw allow 8888    # Jupyter Lab
sudo ufw allow 8501    # Streamlit
sudo ufw allow 8000    # Ollama
sudo ufw allow 9090    # Prometheus
sudo ufw allow 3000    # Grafana
sudo ufw allow 5601    # Kibana

# Enable firewall
sudo ufw --force enable
