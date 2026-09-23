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
    

def test_change_password(client):
    client.post("/api/auth/register", json={"email": "passchange@test.com", "password": "TestPassword123!", "full_name": "Test User", "organization_name": "Test Org", "role": "INSPECTOR"})
    login_resp = client.post("/api/auth/login", data={"username": "passchange@test.com", "password": "TestPassword123!"})
    token = login_resp.json()["access_token"]
    
    resp = client.post("/api/auth/change-password", json={"current_password": "TestPassword123!", "new_password": "NewTestPassword123!", "confirm_password": "NewTestPassword123!"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    
    login_resp2 = client.post("/api/auth/login", data={"username": "passchange@test.com", "password": "NewTestPassword123!"})
    assert login_resp2.status_code == 200
