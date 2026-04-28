from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
import pandas as pd
import joblib
import scipy.sparse
import time
import os
import glob
from src.data_loader import load_data
from src.als_model import load_als_model
from src.content_processor import load_analyzed_texts, load_tfidf
from src.recommendation import hybrid_recommend, get_user_watch_history
from src.config import MODEL_PKL, CONTENT_DATA_PKL, ITEM_USER_NPZ, MAPS_PKL, PREPROCESSED_DIR, TFIDF_DIR, USER_ITEMS_NPZ
import asyncpg
from src.user_preferences import get_user_preferences

class RecommendRequest(BaseModel):
    user_id: int
    count: int = 10

df, als_model, user_map, item_map, item_map_inv, item_user, user_items = None, None, None, None, None, None, None
content_df, grp_meta, rep_map, asset_to_group, analyzed_texts, tfidf, group_vectors, tfidf_matrix, group_ids = None, None, None, None, None, None, None, None, None
user_watched, user_groups, user_watched_programs, asset_to_poster, user_genre_pref, user_country_pref, asset_to_genre, asset_to_country, asset_to_super = None, None, None, None, None, None, None, None, None

async def load_file_async(path, load_func):
    """비동기 파일 로드, Redis 캐싱 제거"""
    return await asyncio.to_thread(load_func, path)

async def background_load():
    """대규모 데이터 백그라운드 로드"""
    global user_items, tfidf_matrix
    try:
        print(f"{USER_ITEMS_NPZ}에서 user_items 로드 중")
        user_items = scipy.sparse.load_npz(USER_ITEMS_NPZ)
        print(f"✅ user_items 로드 완료, shape: {user_items.shape}")
    except Exception as e:
        print(f"❌ user_items 로드 실패: {str(e)}")
        raise
    tfidf_parts = sorted(glob.glob(os.path.join(TFIDF_DIR, "tfidf_part_*.npz")))
    if not tfidf_parts:
        raise FileNotFoundError(f"{TFIDF_DIR}에 tfidf_part_*.npz 파일이 없습니다")
    tfidf_matrices = []
    for part_file in tfidf_parts:
        try:
            part_matrix = scipy.sparse.load_npz(part_file)
            tfidf_matrices.append(part_matrix)
            print(f"{part_file} 로드 완료, shape: {part_matrix.shape}")
        except Exception as e:
            print(f"{part_file} 로드 오류: {str(e)}")
            raise
    tfidf_matrix = scipy.sparse.vstack(tfidf_matrices)
    print(f"✅ TF-IDF 행렬 병합 완료, shape: {tfidf_matrix.shape}")
    print("✅ 백그라운드 데이터 로드 완료")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, als_model, user_map, item_map, item_map_inv, item_user, user_items
    global group_vectors, tfidf_matrix, group_ids, rep_map, asset_to_group
    global user_watched, user_groups, asset_to_super, user_watched_programs
    global asset_to_poster, user_genre_pref, user_country_pref, asset_to_genre
    global asset_to_country, asset_to_keyword  # asset_to_keyword 추가
    
    print("🔄 Loading data and models...")
    
    start_time = time.time()
    tasks = [
        asyncio.to_thread(load_als_model),
        load_file_async(CONTENT_DATA_PKL, joblib.load),
        load_file_async(ITEM_USER_NPZ, scipy.sparse.load_npz),
        load_file_async(MAPS_PKL, joblib.load),
        asyncio.to_thread(load_analyzed_texts),
        asyncio.to_thread(load_tfidf)
    ]
    
    results = await asyncio.gather(*tasks)
    print(f"초기 데이터 로드 완료: {time.time() - start_time:.2f}초")
    
    als_model, user_map, item_map = results[0]
    item_map_inv = {i: a for a, i in item_map.items()}
    content_data = results[1]
    item_user = results[2]
    content_df = content_data["content_df"]
    grp_meta = content_data["grp_meta"]
    rep_map = content_data["rep_map"]
    asset_to_group = content_data["asset_to_group"]
    analyzed_texts = results[4]
    tfidf, group_vectors = results[5]
    group_ids = list(group_vectors.keys())
    maps = results[3]
    user_watched = maps["user_watched"]
    user_groups = maps["user_groups"]
    user_watched_programs = maps["user_watched_programs"]
    user_genre_pref = maps["user_genre_pref"]
    user_country_pref = maps["user_country_pref"]
    asset_to_genre = maps["asset_to_genre"]
    asset_to_country = maps["asset_to_country"]
    asset_to_poster = maps["asset_to_poster"]
    asset_to_super = content_df.set_index("asset_id")["super_asset_nm"].to_dict()

    # 키워드 정보 로드 추가
    try:
        # PostgreSQL에서 키워드 정보 직접 가져오기
        conn = await asyncpg.connect(DB_CONNECTION_STRING)
        keyword_records = await conn.fetch(
            "SELECT asset_id, keywords FROM content_metadata WHERE keywords IS NOT NULL"
        )
        await conn.close()
        
        asset_to_keyword = {}
        for record in keyword_records:
            asset_id = record['asset_id']
            keywords = record['keywords'].split(',') if record['keywords'] else []
            asset_to_keyword[asset_id] = keywords
            
        print(f"✅ Loaded keyword data for {len(asset_to_keyword)} assets")
    except Exception as e:
        print(f"⚠️ Warning: Failed to load keyword data: {str(e)}")
        asset_to_keyword = {}  # 실패 시 빈 딕셔너리로 초기화

    await background_load()

    print(f"item_map 크기: {len(item_map)}")
    print(f"item_map_inv 최대 인덱스: {max(item_map_inv.keys()) if item_map_inv else 'N/A'}")
    print(f"user_items 모양: {user_items.shape if user_items is not None else 'None'}")
    print(f"als_model.item_factors 모양: {als_model.item_factors.shape if als_model is not None else 'None'}")
    
    print("✅ 초기화 완료")
    yield
    print("✅ 종료 완료")

app = FastAPI(lifespan=lifespan)

@app.get("/recommend/{user_index}")
async def recommend_get(user_index: int):
    if user_index not in user_map:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    user_df = await asyncio.to_thread(load_data, user_index=user_index, core_only=True)
    watch_history = get_user_watch_history(user_index, user_df, asset_to_super, top_n=10)
    recs = hybrid_recommend(
        user_index, user_df, als_model, user_items, user_map, item_map, item_map_inv,
        group_vectors, tfidf_matrix, group_ids, rep_map, asset_to_group,
        user_watched, user_groups, asset_to_super, user_watched_programs,
        asset_to_poster, user_genre_pref, user_country_pref, asset_to_genre, asset_to_country,
        K=8  # 추천 목록 최대 8개로 제한
    )
    
    # 텍스트 응답 생성
    response = "[시청한 목록]\n"
    for i, title in enumerate(watch_history, 1):
        response += f"{i}. {title}\n"  # watch_history는 문자열 리스트이므로 바로 사용
    response += "\n[추천 목록]\n"
    for i, row in enumerate(recs, 1):
        response += f"{i}. {row[1]}\n"  # recs는 튜플 리스트이므로 row[1]로 제목 추출
    
    return PlainTextResponse(response)

@app.post("/recommendations")
async def get_recommendations(request: RecommendRequest):
    user_id = request.user_id
    
    # 1. 사용자 시청 기록 확인
    user_history = get_user_watch_history(user_id, df, asset_to_super)
    
    # 시청 기록이 없는 신규 사용자 확인
    if not user_history:
        # 2. 사용자 선호도 정보 가져오기
        user_preferences = await get_user_preferences(user_id)
        
        # 3. 선호도 기반 추천 생성
        recommendations = await recommend_for_new_user(
            user_id, 
            df, 
            user_preferences, 
            asset_to_genre, 
            asset_to_keyword,
            asset_to_poster,
            K=request.count
        )
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "user_type": "new",
            "preferences": user_preferences
        }
    
    # 4. 기존 사용자는 하이브리드 추천 사용
    recommendations = hybrid_recommend(
        user_id, df, als_model, user_items, user_map, item_map, item_map_inv,
        group_vectors, tfidf_matrix, group_ids, rep_map, asset_to_group,
        user_watched, user_groups, asset_to_super, user_watched_programs,
        asset_to_poster, user_genre_pref, user_country_pref, asset_to_genre,
        asset_to_country, K=request.count
    )
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "user_type": "existing",
        "watch_history": user_history
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)