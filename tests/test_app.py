from app import app

def test_index():
    test_client = app.test_client()

    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Hello, CI/CD!" in response.data