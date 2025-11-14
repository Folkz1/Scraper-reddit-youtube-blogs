"""
Gerenciador de proxies (Apify + gratuitos) para contornar bloqueios do YouTube
"""
import requests
import random
from typing import Optional, Dict, List
import time
import os

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.last_fetch = 0
        self.fetch_interval = 300  # 5 minutos
        self.apify_token = os.getenv('APIFY_API_TOKEN')
        
    def fetch_free_proxies(self) -> List[str]:
        """Busca lista de proxies gratuitos"""
        proxy_list = []
        
        try:
            # Fonte 1: ProxyScrape
            response = requests.get(
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                timeout=10
            )
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                proxy_list.extend([f'http://{p.strip()}' for p in proxies if p.strip()])
        except:
            pass
        
        try:
            # Fonte 2: Free-Proxy-List
            response = requests.get(
                'https://www.proxy-list.download/api/v1/get?type=http',
                timeout=10
            )
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                proxy_list.extend([f'http://{p.strip()}' for p in proxies if p.strip()])
        except:
            pass
        
        # Remove duplicatas
        proxy_list = list(set(proxy_list))
        
        # Limita a 50 proxies
        return proxy_list[:50] if proxy_list else []
    
    def get_proxies(self) -> List[str]:
        """Retorna lista de proxies (atualiza se necessário)"""
        current_time = time.time()
        
        # Atualiza lista se passou o intervalo ou está vazia
        if not self.proxies or (current_time - self.last_fetch) > self.fetch_interval:
            print("🔄 Buscando proxies gratuitos...")
            self.proxies = self.fetch_free_proxies()
            self.last_fetch = current_time
            print(f"✅ {len(self.proxies)} proxies encontrados")
        
        return self.proxies
    
    def get_apify_proxy(self, proxy_type: str = "RESIDENTIAL") -> Optional[Dict[str, str]]:
        """
        Retorna proxy do Apify (pago mas muito confiável)
        proxy_type: RESIDENTIAL (melhor) ou DATACENTER (mais barato)
        """
        if not self.apify_token:
            return None
        
        # Formato: http://groups-RESIDENTIAL:TOKEN@proxy.apify.com:8000
        proxy_url = f"http://groups-{proxy_type}:{self.apify_token}@proxy.apify.com:8000"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Retorna um proxy aleatório no formato do requests"""
        proxies = self.get_proxies()
        
        if not proxies:
            return None
        
        proxy = random.choice(proxies)
        return {
            'http': proxy,
            'https': proxy
        }
    
    def test_proxy(self, proxy_dict: Dict[str, str], timeout: int = 5) -> bool:
        """Testa se um proxy está funcionando"""
        try:
            response = requests.get(
                'https://www.youtube.com',
                proxies=proxy_dict,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return response.status_code == 200
        except:
            return False

# Instância global
proxy_manager = ProxyManager()
