#!/usr/bin/env python3
"""
SSL Connection Test Script
Tests SSL connection to Mini App server
"""
import requests
import ssl
import socket
import sys
from urllib3.util.ssl_ import create_urllib3_context

def test_ssl_connection(host, port):
    """Test SSL connection to host:port"""
    print(f"🔍 Testing SSL connection to {host}:{port}")
    print("=" * 50)
    
    # Test 1: Basic socket connection
    print("1. Testing basic socket connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ Socket connection successful")
        else:
            print(f"❌ Socket connection failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Socket connection error: {e}")
        return False
    
    # Test 2: SSL context creation
    print("\n2. Testing SSL context creation...")
    try:
        context = ssl.create_default_context()
        print("✅ SSL context created successfully")
    except Exception as e:
        print(f"❌ SSL context creation failed: {e}")
        return False
    
    # Test 3: SSL handshake
    print("\n3. Testing SSL handshake...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        cert = ssl_sock.getpeercert()
        ssl_sock.close()
        
        print("✅ SSL handshake successful")
        print(f"   Certificate subject: {cert.get('subject', 'Unknown')}")
        print(f"   Certificate issuer: {cert.get('issuer', 'Unknown')}")
        print(f"   Certificate version: {cert.get('version', 'Unknown')}")
        
    except ssl.SSLError as e:
        print(f"❌ SSL handshake failed: {e}")
        return False
    except Exception as e:
        print(f"❌ SSL handshake error: {e}")
        return False
    
    # Test 4: HTTP request with different SSL settings
    print("\n4. Testing HTTP requests...")
    
    test_urls = [
        f"https://{host}:{port}",
        f"https://{host}:{port}/api/secure/create-link"
    ]
    
    ssl_options = [
        ("Default verification", True),
        ("No verification", False),
        ("Custom CA bundle", "/etc/ssl/certs/ca-certificates.crt"),
        ("Custom CA bundle (macOS)", "/etc/ssl/cert.pem"),
    ]
    
    for url in test_urls:
        print(f"\n   Testing URL: {url}")
        for name, verify in ssl_options:
            try:
                response = requests.get(url, verify=verify, timeout=5)
                print(f"   ✅ {name}: Status {response.status_code}")
            except requests.exceptions.SSLError as e:
                print(f"   ❌ {name}: SSL Error - {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"   ❌ {name}: Connection Error - {e}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
    
    return True

def test_certificate_chain(host, port):
    """Test certificate chain validation"""
    print(f"\n🔐 Testing certificate chain for {host}:{port}")
    print("=" * 50)
    
    try:
        import ssl
        import socket
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        cert = ssl_sock.getpeercert()
        ssl_sock.close()
        
        print("Certificate details:")
        print(f"  Subject: {cert.get('subject', 'Unknown')}")
        print(f"  Issuer: {cert.get('issuer', 'Unknown')}")
        print(f"  Version: {cert.get('version', 'Unknown')}")
        print(f"  Serial Number: {cert.get('serialNumber', 'Unknown')}")
        print(f"  Not Before: {cert.get('notBefore', 'Unknown')}")
        print(f"  Not After: {cert.get('notAfter', 'Unknown')}")
        
        # Check if certificate is from GlobalSign
        issuer = str(cert.get('issuer', ''))
        if 'GlobalSign' in issuer:
            print("✅ Certificate is from GlobalSign")
        else:
            print(f"⚠️  Certificate issuer: {issuer}")
        
        return True
        
    except Exception as e:
        print(f"❌ Certificate chain test failed: {e}")
        return False

if __name__ == "__main__":
    host = "bot.bunter.ru"
    port = 4477
    
    print("🚀 SSL Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test basic connection
    if test_ssl_connection(host, port):
        print("\n✅ Basic SSL connection test passed")
    else:
        print("\n❌ Basic SSL connection test failed")
        sys.exit(1)
    
    # Test certificate chain
    if test_certificate_chain(host, port):
        print("\n✅ Certificate chain test passed")
    else:
        print("\n❌ Certificate chain test failed")
    
    print("\n🎉 SSL diagnostic completed!")
    print("\n💡 If you see SSL errors, try:")
    print("   1. Set SSL_VERIFY_CERT=false in .env")
    print("   2. Update your CA certificates")
    print("   3. Check if the certificate is properly installed on the server")