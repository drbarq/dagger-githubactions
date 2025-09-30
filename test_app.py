import pytest
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_endpoint(client):
    """Test the main hello endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Hello, World!'
    assert 'secret' in data

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_secret_from_env(client, monkeypatch):
    """Test that secret is read from environment"""
    monkeypatch.setenv('SECRET_MESSAGE', 'test-secret-value')
    # Need to reload the app to pick up the new env var
    from app import app as test_app
    test_app.config['TESTING'] = True
    with test_app.test_client() as test_client:
        response = test_client.get('/')
        data = response.get_json()
        assert data['secret'] == 'test-secret-value'