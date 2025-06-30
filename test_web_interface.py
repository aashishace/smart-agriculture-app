#!/usr/bin/env python3
"""
Test Web Interface for Disease Detection
"""

import requests
import json
import os
from PIL import Image, ImageDraw
import time

def create_test_image_for_web():
    """Create a test image for web upload."""
    img = Image.new('RGB', (300, 300), (34, 139, 34))  # Green background
    draw = ImageDraw.Draw(img)
    
    # Add some brown spots to simulate disease
    for i in range(8):
        x, y = 50 + i*25, 50 + (i%3)*25
        draw.ellipse([x, y, x+15, y+15], fill=(139, 35, 35))
    
    test_path = "test_disease_upload.jpg"
    img.save(test_path)
    return test_path

def test_disease_scanner_endpoint():
    """Test the disease scanner web endpoint."""
    
    print("🌐 TESTING WEB INTERFACE ENDPOINTS")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Access disease scanner page
    print("\n1. Testing Disease Scanner Page Access:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/ai/disease-scanner", timeout=10)
        if response.status_code == 200:
            print("✅ Disease scanner page accessible")
            print(f"   Status: {response.status_code}")
            print(f"   Content length: {len(response.content)} bytes")
        else:
            print(f"❌ Page access failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Test disease detection API endpoint
    print("\n2. Testing Disease Detection API:")
    print("-" * 35)
    
    # Create test image
    test_image_path = create_test_image_for_web()
    
    try:
        with open(test_image_path, 'rb') as img_file:
            files = {'image': img_file}
            data = {'crop_id': '1'}  # Assuming crop ID 1 exists
            
            response = requests.post(
                f"{base_url}/ai/detect-disease",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Disease detection API working")
                print(f"   Disease: {result['result']['disease']}")
                print(f"   Confidence: {result['result']['confidence']:.2%}")
                print(f"   Healthy: {result['result']['is_healthy']}")
                print(f"   Severity: {result['result']['severity']}")
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ API request error: {e}")
    except FileNotFoundError:
        print("❌ Test image creation failed")
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
    
    # Test 3: Test disease history page
    print("\n3. Testing Disease History Page:")
    print("-" * 33)
    
    try:
        response = requests.get(f"{base_url}/ai/disease-history", timeout=10)
        if response.status_code == 200:
            print("✅ Disease history page accessible")
            print(f"   Status: {response.status_code}")
        else:
            print(f"❌ History page access failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    return True

def test_dashboard_access():
    """Test dashboard access after fixing template."""
    
    print("\n🏠 TESTING DASHBOARD ACCESS")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard accessible without template errors")
            print(f"   Status: {response.status_code}")
            print(f"   Content length: {len(response.content)} bytes")
            
            # Check for key dashboard elements
            content = response.text.lower()
            elements = [
                ("quick actions", "quick actions" in content),
                ("weather info", "weather" in content),
                ("crop management", "crop" in content),
                ("disease scanner", "disease" in content)
            ]
            
            print("\n   Dashboard Elements:")
            for element, present in elements:
                status = "✅" if present else "❌"
                print(f"   {status} {element.title()}")
                
        elif response.status_code == 302:
            print("⚠️  Dashboard redirected (likely to login)")
            print("   This is expected if not logged in")
        else:
            print(f"❌ Dashboard access failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

def check_app_status():
    """Check if the Flask app is running."""
    
    print("🔍 CHECKING APPLICATION STATUS")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ Application is running on {base_url}")
        print(f"   Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException:
        print("❌ Application is not accessible")
        print("   Make sure Flask app is running on port 5000")
        return False

if __name__ == "__main__":
    print("🧪 SMART AGRICULTURE - WEB INTERFACE TESTING")
    print("=" * 60)
    
    # Check if app is running
    if not check_app_status():
        print("\n⚠️  Please start the Flask application first:")
        print("   python run.py")
        exit(1)
    
    # Wait a moment for app to fully initialize
    time.sleep(2)
    
    # Test dashboard
    test_dashboard_access()
    
    # Test disease detection web interface
    test_disease_scanner_endpoint()
    
    print("\n🎯 WEB INTERFACE TESTING COMPLETED!")
    print("=" * 60)
