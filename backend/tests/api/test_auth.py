import pytest

def test_registration_and_login(client):
    # Test registration
    resp = client.post("/api/auth/register", json={"email": "newuser@test.com", "password": "TestPassword123!", "full_name": "New User", "organization_name": "Test Org", "role": "INSPECTOR"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "newuser@test.com"
    
    # Test duplicate registration
    resp = client.post("/api/auth/register", json={"email": "newuser@test.com", "password": "TestPassword123!", "full_name": "New User", "organization_name": "Test Org", "role": "INSPECTOR"})
    assert resp.status_code == 400
    
    # Test login
    resp = client.post("/api/auth/login", data={"username": "newuser@test.com", "password": "TestPassword123!"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_invalid_credentials(client):
    resp = client.post("/api/auth/login", data={"username": "fake@test.com", "password": "bad"})
    assert resp.status_code == 400
    
