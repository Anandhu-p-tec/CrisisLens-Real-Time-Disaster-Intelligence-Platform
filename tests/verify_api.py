import asyncio
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the /health endpoint"""
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["status"] == "ok"
    print("✓ Health endpoint works correctly")

def test_routes_registered():
    """Test that all routes are registered"""
    routes = [route.path for route in app.routes]
    print(f"\nRegistered routes ({len(routes)} total):")
    for route in sorted(routes):
        print(f"  {route}")
    
    required_routes = ["/health", "/events", "/events/{post_id}", "/ws/feed"]
    for route in required_routes:
        assert route in routes, f"Missing route: {route}"
    print("✓ All required routes registered")

if __name__ == "__main__":
    test_health_endpoint()
    test_routes_registered()
    print("\n✓ All API verification tests passed!")
