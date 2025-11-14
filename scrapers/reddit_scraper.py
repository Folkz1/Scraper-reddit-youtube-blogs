import praw
import os
from typing import Dict, List
from datetime import datetime

# Configuração do Reddit (pode usar sem autenticação para testes)
def get_reddit_client():
    """Cria cliente Reddit (funciona sem credenciais para leitura básica)"""
    try:
        # Tenta usar credenciais se disponíveis
        client_id = os.getenv('REDDIT_CLIENT_ID', '')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'ScraperBot/1.0')
        
        if client_id and client_secret:
            return praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
        else:
            # Modo somente leitura (sem autenticação)
            return praw.Reddit(
                client_id='',
                client_secret='',
                user_agent=user_agent
            )
    except Exception as e:
        raise Exception(f"Erro ao criar cliente Reddit: {str(e)}")

def extract_post_id(url: str) -> str:
    """Extrai o ID do post de uma URL do Reddit"""
    import re
    # Formato: reddit.com/r/subreddit/comments/POST_ID/titulo
    match = re.search(r'/comments/([a-z0-9]+)', url)
    if match:
        return match.group(1)
    raise ValueError("URL do Reddit inválida")

async def scrape_reddit(
    url: str,
    max_comments: int = 10,
    sort_by: str = "top"
) -> Dict:
    """
    Scrape de posts do Reddit com comentários
    
    Args:
        url: URL do post do Reddit
        max_comments: Número máximo de comentários top-level
        sort_by: Ordenação dos comentários (top, best, new, controversial)
    """
    try:
        reddit = get_reddit_client()
        
        # Extrai ID do post
        post_id = extract_post_id(url)
        
        # Busca o post
        submission = reddit.submission(id=post_id)
        
        # Ordena comentários
        if sort_by == "top":
            submission.comment_sort = "top"
        elif sort_by == "best":
            submission.comment_sort = "best"
        elif sort_by == "new":
            submission.comment_sort = "new"
        elif sort_by == "controversial":
            submission.comment_sort = "controversial"
        
        # Carrega comentários
        submission.comments.replace_more(limit=0)  # Remove "load more comments"
        
        # Extrai comentários top-level
        comments = []
        for comment in submission.comments[:max_comments]:
            if hasattr(comment, 'body'):  # Verifica se é um comentário válido
                comments.append({
                    "author": str(comment.author) if comment.author else "[deleted]",
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                    "replies_count": len(comment.replies) if hasattr(comment, 'replies') else 0
                })
        
        # Monta resposta
        return {
            "title": submission.title,
            "author": str(submission.author) if submission.author else "[deleted]",
            "subreddit": str(submission.subreddit),
            "selftext": submission.selftext,  # Conteúdo do post (se for texto)
            "url": url,
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
            "is_self": submission.is_self,  # True se for post de texto
            "link_url": submission.url if not submission.is_self else None,  # URL externa se houver
            "comments": comments,
            "word_count": len(submission.selftext.split()) + sum(len(c['body'].split()) for c in comments)
        }
    
    except Exception as e:
        raise Exception(f"Erro ao buscar post do Reddit: {str(e)}")
