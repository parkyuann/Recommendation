import pickle
import numpy as np
from scipy import sparse
from implicit.als import AlternatingLeastSquares
from src.config import MODEL_PKL
import joblib

def load_als_model():
    """
    ALS 모델과 매핑 데이터를 로드합니다.
    Returns:
        tuple: (als_model, user_map, item_map)
    """
    try:
        with open(MODEL_PKL, "rb") as f:
            payload = joblib.load(f)
        return payload["model"], payload["user_map"], payload["item_map"]
    except Exception as e:
        raise RuntimeError(f"Failed to load ALS model from {MODEL_PKL}: {str(e)}")

def get_als_recommendations(als_model, user_items, user_map, item_map_inv, user_index, N=100):
    """
    ALS 모델을 사용해 추천 생성
    Args:
        als_model: 학습된 ALS 모델
        user_items: 사용자-아이템 희소 행렬
        user_map: 사용자 인덱스 매핑
        item_map_inv: 아이템 인덱스 역매핑
        user_index: 추천 대상 사용자 ID
        N: 추천 수
    Returns:
        tuple: (추천 asset_id 리스트, 점수 배열)
    """
    u_idx = user_map[user_index]
    item_ids, scores = als_model.recommend(u_idx, user_items[u_idx], N=N, filter_already_liked_items=True)
    rec_asset_ids, rec_scores = [], []
    for idx, sc in zip(item_ids, scores):
        aid = item_map_inv.get(idx)
        if aid is not None:
            rec_asset_ids.append(aid)
            rec_scores.append(sc)
    return rec_asset_ids, np.array(rec_scores)