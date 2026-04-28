import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from src.als_model import get_als_recommendations

def hybrid_recommend(
    user_index: int, df, als_model, user_items, user_map, item_map, item_map_inv,
    group_vectors, tfidf_matrix, group_ids, rep_map, asset_to_group,
    user_watched, user_groups, asset_to_super, user_watched_programs,
    asset_to_poster, user_genre_pref, user_country_pref, asset_to_genre,
    asset_to_country, N=100, M=100, K=10, w_als=0.2, w_cont=0.3,
    w_genre=0.3, w_country=0.2
):
    assert abs(w_als + w_cont + w_genre + w_country - 1) < 1e-6, "가중치 합은 1이어야 합니다."
    watched = set(user_watched.get(user_index, []))
    user_group_ids = user_groups.get(user_index, [])
    watched_programs = user_watched_programs.get(user_index, set())

    # ALS 기반 추천
    als_assets, _ = get_als_recommendations(als_model, user_items, user_map, item_map_inv, user_index, N=N)

    # 콘텐츠 기반 추천
    if user_group_ids:
        user_vecs = sparse.vstack([group_vectors[g] for g in user_group_ids])
        sims = cosine_similarity(tfidf_matrix, user_vecs).max(axis=1)
        rank_idx = np.argsort(sims)[::-1]
        rank_idx = [i for i in rank_idx if group_ids[i] not in user_group_ids]
        top_groups = [group_ids[i] for i in rank_idx[:M]]
        content_assets = [rep_map[g] for g in top_groups]
    else:
        sims, content_assets = np.zeros(len(group_ids)), []

    # 후보 아이템 생성
    candidates = list(set(als_assets + content_assets) - watched)
    candidates = [aid for aid in candidates if asset_to_super.get(aid) not in watched_programs]
    if not candidates:
        return []

    # 하이브리드 스코어 계산
    u_idx = user_map[user_index]
    uf = als_model.user_factors[u_idx]
    cf_idx = [item_map[a] for a in candidates]
    cf_mat = als_model.item_factors[cf_idx]
    als_raw = (uf @ cf_mat.T).flatten()
    range_val = np.ptp(als_raw)  # == als_raw.max() - als_raw.min()
    als_norm  = (als_raw - als_raw.min()) / (range_val or 1)
    cont_scores = np.array([sims[asset_to_group.get(a, -1)] if a in asset_to_group else 0 for a in candidates])
    genre_scores = np.array([user_genre_pref.get(user_index, {}).get(asset_to_genre.get(a, None), 0.0) for a in candidates])
    country_scores = np.array([user_country_pref.get(user_index, {}).get(asset_to_country.get(a, None), 0.0) for a in candidates])
    hybrid = (w_als * als_norm + w_cont * cont_scores + w_genre * genre_scores + w_country * country_scores)

    # 결과 정렬
    candidates_with_scores = [
        (aid, hybrid[i], asset_to_poster.get(aid, None) is not None, asset_to_poster.get(aid, None))
        for i, aid in enumerate(candidates)
    ]
    candidates_with_scores.sort(key=lambda x: (not x[2], -x[1]))

    # 중복 제거 및 상위 K개 반환
    seen_super, result = set(), []
    for aid, score, has_poster, poster_url in candidates_with_scores:
        sup = asset_to_super.get(aid)
        if sup and sup not in seen_super:
            result.append((aid, sup, score, poster_url))
            seen_super.add(sup)
            if len(result) == K:
                break
    return result

def get_user_watch_history(user_index: int, df, asset_to_super, top_n=10):
    user_data = df[df["user_index"] == user_index]
    if user_data.empty:
        return []
    # 디버깅: asset_to_super 샘플 출력
    print(f"asset_to_super 샘플: {dict(list(asset_to_super.items())[:5])}")
    
    watch_counts = user_data.groupby("asset_id").size().reset_index(name="count")
    watch_counts["super_asset_nm"] = watch_counts["asset_id"].map(asset_to_super)
    # 디버깅: watch_counts 확인
    print(f"watch_counts 샘플:\n{watch_counts.head().to_string()}")
    
    watch_counts = watch_counts.groupby("super_asset_nm").agg({"count": "sum"}).reset_index()
    watch_counts = watch_counts.sort_values("count", ascending=False).head(top_n)
    # 디버깅: 최종 제목 리스트 확인
    print(f"최종 시청 목록: {watch_counts['super_asset_nm'].values.tolist()}")
    
    return watch_counts["super_asset_nm"].values.tolist()

async def recommend_for_new_user(
    user_id: int, 
    df, 
    user_preferences: Dict[str, List[str]], 
    asset_to_genre: Dict[int, List[str]], 
    asset_to_keyword: Dict[int, List[str]], 
    asset_to_poster: Dict[int, str],
    K: int = 10
) -> List[Dict]:
    """
    신규 사용자를 위한 추천 생성
    
    Args:
        user_id: 사용자 ID
        df: 데이터프레임
        user_preferences: 사용자 선호 장르 및 키워드
        asset_to_genre: 콘텐츠별 장르 매핑
        asset_to_keyword: 콘텐츠별 키워드 매핑
        asset_to_poster: 콘텐츠별 포스터 URL 매핑
        K: 추천 개수
        
    Returns:
        List[Dict]: 추천 콘텐츠 목록
    """
    import pandas as pd
    import numpy as np
    
    fav_genres = set(user_preferences.get("genres", []))
    fav_keywords = set(user_preferences.get("keywords", []))
    
    # 시청 횟수 정보가 있는 DataFrame 준비
    view_counts = df.groupby("asset_id").size().reset_index(name="view_count")
    
    # 장르 및 키워드 매칭 점수 계산
    candidates = []
    for asset_id in df["asset_id"].unique():
        asset_genres = set(asset_to_genre.get(asset_id, []))
        asset_keywords = set(asset_to_keyword.get(asset_id, []))
        
        # 장르 일치 점수
        genre_match = len(fav_genres.intersection(asset_genres)) / max(1, len(fav_genres)) if fav_genres else 0
        
        # 키워드 일치 점수
        keyword_match = len(fav_keywords.intersection(asset_keywords)) / max(1, len(fav_keywords)) if fav_keywords else 0
        
        # 종합 점수 (장르와 키워드 매치를 동일한 가중치로 고려)
        match_score = (genre_match + keyword_match) / 2
        
        if match_score > 0:  # 하나라도 일치하는 경우만 후보로 선정
            candidates.append((asset_id, match_score))
    
    # 일치하는 콘텐츠가 없는 경우 가장 인기있는 콘텐츠 추천
    if not candidates:
        top_assets = view_counts.sort_values("view_count", ascending=False)["asset_id"].tolist()[:K]
        result = []
        for asset_id in top_assets:
            super_name = df[df["asset_id"] == asset_id]["super_asset_nm"].iloc[0]
            poster_url = asset_to_poster.get(asset_id, "")
            result.append({
                "asset_id": int(asset_id),
                "super_asset_nm": super_name,
                "poster_url": poster_url,
                "score": 0.0,
                "recommendation_type": "popular"
            })
        return result
    
    # 일치하는 콘텐츠 중에서 시청 횟수로 정렬
    candidate_df = pd.DataFrame(candidates, columns=["asset_id", "match_score"])
    candidate_df = candidate_df.merge(view_counts, on="asset_id")
    
    # 매칭 점수와 시청 횟수를 결합하여 최종 점수 계산
    # 여기서는 매칭 점수에 0.7, 시청 횟수(정규화)에 0.3의 가중치를 줌
    max_views = candidate_df["view_count"].max()
    candidate_df["normalized_views"] = candidate_df["view_count"] / max_views if max_views > 0 else 0
    candidate_df["final_score"] = 0.7 * candidate_df["match_score"] + 0.3 * candidate_df["normalized_views"]
    
    # 최종 점수로 정렬하여 상위 K개 선택
    top_candidates = candidate_df.sort_values("final_score", ascending=False).head(K)
    
    # 결과 포맷팅
    result = []
    for _, row in top_candidates.iterrows():
        asset_id = int(row["asset_id"])
        super_name = df[df["asset_id"] == asset_id]["super_asset_nm"].iloc[0]
        poster_url = asset_to_poster.get(asset_id, "")
        result.append({
            "asset_id": asset_id,
            "super_asset_nm": super_name,
            "poster_url": poster_url,
            "score": float(row["final_score"]),
            "recommendation_type": "preference_based"
        })
    
    return result

print("✅ recommendation.py 초기화 완료")