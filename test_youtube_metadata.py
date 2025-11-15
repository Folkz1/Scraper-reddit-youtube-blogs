"""
Testa o endpoint de metadados do YouTube
"""
import requests

def test_metadata_local():
    """Testa localmente"""
    url = "http://localhost:8001/youtube/metadata"
    
    payload = {
        "url": "https://www.youtube.com/shorts/bfKu9LVqC4Q"
    }
    
    print("Testando endpoint /youtube/metadata localmente...")
    print(f"URL: {payload['url']}\n")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('success'):
            print("SUCESSO!")
            print("=" * 70)
            
            video_data = data['data']
            print(f"Titulo: {video_data.get('title')}")
            print(f"Canal: {video_data.get('channel_title')}")
            print(f"Views: {video_data.get('view_count'):,}")
            print(f"Likes: {video_data.get('like_count'):,}")
            print(f"Comentarios: {video_data.get('comment_count'):,}")
            print(f"Publicado em: {video_data.get('published_at')}")
            print(f"Duracao: {video_data.get('duration_seconds')}s")
            
            if video_data.get('channel_info'):
                print("\nInformacoes do Canal:")
                channel = video_data['channel_info']
                print(f"  Inscritos: {channel.get('subscriber_count'):,}")
                print(f"  Total de videos: {channel.get('video_count'):,}")
                print(f"  Views totais: {channel.get('view_count'):,}")
            
            print("=" * 70)
        else:
            print(f"ERRO: {data.get('error')}")
            
    except Exception as e:
        print(f"ERRO: {e}")

def test_metadata_vps():
    """Testa na VPS"""
    url = "https://scrapers-reddit-youtube-blogs.7exngm.easypanel.host/youtube/metadata"
    
    payload = {
        "url": "https://www.youtube.com/shorts/bfKu9LVqC4Q"
    }
    
    print("\nTestando endpoint /youtube/metadata na VPS...")
    print(f"URL: {payload['url']}\n")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('success'):
            print("SUCESSO!")
            print("=" * 70)
            
            video_data = data['data']
            print(f"Titulo: {video_data.get('title')}")
            print(f"Canal: {video_data.get('channel_title')}")
            print(f"Views: {video_data.get('view_count'):,}")
            print(f"Likes: {video_data.get('like_count'):,}")
            print(f"Comentarios: {video_data.get('comment_count'):,}")
            
            print("=" * 70)
        else:
            print(f"ERRO: {data.get('error')}")
            
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    print("Escolha:")
    print("1 - Testar localmente")
    print("2 - Testar na VPS")
    choice = input("Opcao: ")
    
    if choice == "1":
        test_metadata_local()
    else:
        test_metadata_vps()
