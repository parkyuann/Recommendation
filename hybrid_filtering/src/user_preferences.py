# 새 파일을 생성하여 아래 코드를 추가하세요

import asyncpg
from typing import Dict, List, Optional

async def get_user_preferences(user_id: int) -> Dict[str, List[str]]:
    """
    PostgreSQL DB에서 사용자의 선호 장르와 키워드를 가져옵니다.
    
    Args:
        user_id: 사용자 ID
        
    Returns:
        Dict[str, List[str]]: 사용자의 선호 장르와 키워드를 담은 딕셔너리
    """
    from src.config import DB_CONNECTION_STRING
    
    conn = await asyncpg.connect(DB_CONNECTION_STRING)
    
    # PostgreSQL에서는 인용 부호를 다르게 처리하므로 쿼리를 주의해서 작성
    result = await conn.fetchrow(
        'SELECT fav_genre, fav_keyword FROM customer WHERE user_id = $1', 
        user_id
    )
    
    await conn.close()
    
    if not result:
        return {"genres": [], "keywords": []}
    
    # DB에 저장된 형식에 따라 파싱 방식을 조정해야 할 수 있음
    fav_genre = result['fav_genre']
    fav_keyword = result['fav_keyword']
    
    genres = fav_genre.split(',') if fav_genre else []
    keywords = fav_keyword.split(',') if fav_keyword else []
    
    return {"genres": genres, "keywords": keywords}