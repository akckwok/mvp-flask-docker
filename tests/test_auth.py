import pytest
from server import create_app
from database import db
from user import User

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    """Test user registration."""
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert response.json['success'] is True

    # Test registering the same user again
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 400
    assert response.json['success'] is False
    assert response.json['message'] == 'Username already exists'

def test_login(client):
    """Test user login."""
    # First, register a user
    client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Test login with correct credentials
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert response.json['success'] is True

    # Test login with incorrect password
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['success'] is False
    assert response.json['message'] == 'Invalid credentials'

    # Test login with non-existent user
    response = client.post('/api/login', json={
        'username': 'nosuchuser',
        'password': 'password'
    })
    assert response.status_code == 401
    assert response.json['success'] is False
    assert response.json['message'] == 'Invalid credentials'
