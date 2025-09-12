#!/usr/bin/env python3
"""
DNS Diagnostic Script
Tests DNS resolution and connectivity
"""
import socket
import requests
import subprocess
import sys
import time
from urllib.parse import urlparse

def test_dns_resolution(hostname):
    """Test DNS resolution for hostname"""
    print(f"🔍 Testing DNS resolution for {hostname}")
    print("=" * 50)
    
    try:
        # Test IPv4 resolution
        ipv4 = socket.gethostbyname(hostname)
        print(f"✅ IPv4: {ipv4}")
    except socket.gaierror as e:
        print(f"❌ IPv4 resolution failed: {e}")
        return False
    
    try:
        # Test IPv6 resolution
        ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)
        print(f"✅ IPv6: {ipv6[0][4][0]}")
    except socket.gaierror:
        print("⚠️  IPv6 resolution not available")
    
    return True

def test_connectivity(hostname, port):
    """Test connectivity to hostname:port"""
    print(f"\n🔌 Testing connectivity to {hostname}:{port}")
    print("=" * 50)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Connection successful to {hostname}:{port}")
            return True
        else:
            print(f"❌ Connection failed to {hostname}:{port} (error: {result})")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_http_requests(hostname, port):
    """Test HTTP requests to hostname:port"""
    print(f"\n🌐 Testing HTTP requests to {hostname}:{port}")
    print("=" * 50)
    
    test_urls = [
        f"http://{hostname}:{port}",
        f"https://{hostname}:{port}",
        f"http://{hostname}:{port}/api/secure/create-link",
        f"https://{hostname}:{port}/api/secure/create-link"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=5, verify=False)
            print(f"✅ Status: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {e}")
        except requests.exceptions.SSLError as e:
            print(f"⚠️  SSL Error: {e}")
        except requests.exceptions.Timeout as e:
            print(f"⏰ Timeout: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_dns_servers():
    """Test DNS servers"""
    print(f"\n🔧 Testing DNS servers")
    print("=" * 50)
    
    # Test with different DNS servers
    dns_servers = [
        "8.8.8.8",      # Google DNS
        "1.1.1.1",      # Cloudflare DNS
        "208.67.222.222" # OpenDNS
    ]
    
    hostname = "bot.bunter.ru"
    
    for dns_server in dns_servers:
        try:
            print(f"Testing with DNS server: {dns_server}")
            # Use nslookup if available
            result = subprocess.run(
                ["nslookup", hostname, dns_server], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ {dns_server}: {hostname} resolved")
                # Extract IP from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Address:' in line and hostname not in line:
                        print(f"   IP: {line.split('Address:')[1].strip()}")
            else:
                print(f"❌ {dns_server}: Resolution failed")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {dns_server}: Timeout")
        except FileNotFoundError:
            print(f"⚠️  nslookup not available, skipping {dns_server}")
        except Exception as e:
            print(f"❌ {dns_server}: Error - {e}")

def suggest_solutions(hostname, port):
    """Suggest solutions based on test results"""
    print(f"\n💡 Рекомендации для {hostname}:{port}")
    print("=" * 50)
    
    print("1. Проверьте DNS настройки:")
    print("   - Убедитесь, что домен зарегистрирован")
    print("   - Проверьте A-записи в DNS")
    print("   - Подождите распространения DNS (до 24 часов)")
    
    print("\n2. Альтернативные решения:")
    print("   - Используйте IP-адрес вместо домена")
    print("   - Настройте локальный hosts файл")
    print("   - Используйте другой домен")
    
    print("\n3. Для тестирования:")
    print("   - Запустите Mini App локально")
    print("   - Используйте localhost вместо домена")
    print("   - Проверьте настройки файрвола")

def test_localhost_alternative():
    """Test localhost alternative"""
    print(f"\n🏠 Testing localhost alternative")
    print("=" * 50)
    
    localhost_urls = [
        "http://localhost:4477",
        "http://127.0.0.1:4477",
        "https://localhost:4477",
        "https://127.0.0.1:4477"
    ]
    
    for url in localhost_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=5, verify=False)
            print(f"✅ Status: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {e}")
        except requests.exceptions.SSLError as e:
            print(f"⚠️  SSL Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    hostname = "bot.bunter.ru"
    port = 4477
    
    print("🔍 DNS и Connectivity Diagnostic Tool")
    print("=" * 50)
    
    # Test DNS resolution
    dns_ok = test_dns_resolution(hostname)
    
    if dns_ok:
        # Test connectivity
        conn_ok = test_connectivity(hostname, port)
        
        if conn_ok:
            # Test HTTP requests
            test_http_requests(hostname, port)
        else:
            print(f"\n❌ Cannot connect to {hostname}:{port}")
            print("   Проверьте, что сервер запущен и порт открыт")
    else:
        print(f"\n❌ Cannot resolve {hostname}")
        print("   Проверьте DNS настройки")
    
    # Test DNS servers
    test_dns_servers()
    
    # Test localhost alternative
    test_localhost_alternative()
    
    # Suggest solutions
    suggest_solutions(hostname, port)
    
    print(f"\n🎉 Диагностика завершена!")

if __name__ == "__main__":
    main()