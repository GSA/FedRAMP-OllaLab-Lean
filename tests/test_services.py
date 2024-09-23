import requests

def test_jupyter_lab():
    response = requests.get('http://localhost:8888')
    assert response.status_code == 200

def test_streamlit():
    response = requests.get('http://localhost:8501')
    assert response.status_code == 200

def test_ollama():
    response = requests.get('http://localhost:8000/health')
    assert response.status_code == 200

def test_neo4j():
    response = requests.get('http://localhost:7474')
    assert response.status_code == 200
