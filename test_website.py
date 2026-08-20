"""
Simple test script to verify RAGForge website functionality
Run this after starting the server manually with: python backend/app/main.py
"""
import requests
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing /api/health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check PASSED")
            print(f"   - Status: {data['status']}")
            print(f"   - Ollama Available: {data['ollama']['available']}")
            print(f"   - Documents: {data['documents']['count']}")
            return True
        else:
            print(f"❌ Health check FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check FAILED: {e}")
        return False

def test_documents_list():
    """Test documents list endpoint"""
    print("\n🔍 Testing /api/documents endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            doc_count = len(data) if isinstance(data, list) else len(data.get('documents', []))
            print(f"✅ Documents list PASSED")
            print(f"   - Documents count: {doc_count}")
            return True
        else:
            print(f"❌ Documents list FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Documents list FAILED: {e}")
        return False

def test_frontend():
    """Test frontend is being served"""
    print("\n🔍 Testing frontend (/)...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "root" in content and "html" in content.lower():
                print(f"✅ Frontend PASSED")
                print(f"   - HTML page served correctly")
                return True
            else:
                print(f"❌ Frontend FAILED: Unexpected content")
                return False
        else:
            print(f"❌ Frontend FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend FAILED: {e}")
        return False

def test_api_docs():
    """Test API documentation"""
    print("\n🔍 Testing /api/docs (Swagger UI)...")
    try:
        response = requests.get(f"{BASE_URL}/api/docs", timeout=5)
        if response.status_code == 200:
            print(f"✅ API Docs PASSED")
            return True
        else:
            print(f"❌ API Docs FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Docs FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 RAGForge Website Testing")
    print("=" * 60)
    print(f"\nTesting against: {BASE_URL}")
    print("\nMake sure the server is running first:")
    print("  cd backend && python app/main.py")
    print("\nWaiting 3 seconds for you to start the server...")
    time.sleep(3)
    
    results = {
        "Health Check": test_health(),
        "Documents API": test_documents_list(),
        "Frontend": test_frontend(),
        "API Docs": test_api_docs()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s}: {status}")
    
    print(f"\n🎯 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED! Website is working correctly!")
        print("\n📍 Access points:")
        print(f"   - Frontend: {BASE_URL}")
        print(f"   - API Docs: {BASE_URL}/api/docs")
        print(f"   - Health: {BASE_URL}/api/health")
        return 0
    else:
        print("\n⚠️  Some tests FAILED. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
