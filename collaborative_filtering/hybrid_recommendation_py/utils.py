#!/usr/bin/env python
# utils.py ─ 공통 함수 모음
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from sklearn.preprocessing import MinMaxScaler
from implicit.als import AlternatingLeastSquares


# ─────────────────────────────────────────────────────────────
# 1) 데이터 전처리
# ─────────────────────────────────────────────────────────────
def preprocess_data(df: pd.DataFrame, vod_data: pd.DataFrame) -> pd.DataFrame:
    """
    * completion_rate  : 시청 완료율
    * normalized_time  : 정규화된 시청 시간
    * interaction_strength : 가중 합산 강도
    """
    df = df.merge(
        vod_data[["asset_id", "genre", "category_l1", "category_l2",
                  "super_asset_nm"]],
        on="asset_id", how="left"
    )
    # 완료율
    df["completion_rate"] = (df["use_tms"] / df["disp_rtm"]).clip(0, 1)

    # 정규화된 시청 시간
    scaler = MinMaxScaler()
    df["normalized_time"] = scaler.fit_transform(df[["use_tms"]])

    # 상호작용 강도
    df["interaction_strength"] = (
        0.7 * df["completion_rate"] + 0.3 * df["normalized_time"]
    )

    # 파생-시간 피처
    df["strt_dt"] = pd.to_datetime(df["strt_dt"])
    df["hour"]       = df["strt_dt"].dt.hour
    df["weekday"]    = df["strt_dt"].dt.weekday
    df["weekday_kr"] = (
        df["weekday"]
        .map({0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"})
    )

    return df


# ─────────────────────────────────────────────────────────────
# 2) ALS 모델 학습
# ─────────────────────────────────────────────────────────────
def train_optimized_als(
    processed_df: pd.DataFrame,
    factors: int = 150,
    regularization: float = 0.05,
    iterations: int = 30
):
    """AlternatingLeastSquares 학습 & 매핑 생성"""
    users, user_idx = np.unique(processed_df["sha2_hash"], return_inverse=True)
    items, item_idx = np.unique(processed_df["asset_id"], return_inverse=True)

    data = processed_df["interaction_strength"].values
    mat  = coo_matrix((data, (item_idx, user_idx)))  # item×user

    als_model = AlternatingLeastSquares(
        factors=factors,
        regularization=regularization,
        iterations=iterations,
        calculate_training_loss=True,
        use_gpu=False
    )
    als_model.fit(mat)

    user2idx = {u: i for i, u in enumerate(users)}
    item2idx = {it: i for i, it in enumerate(items)}
    return als_model, user2idx, item2idx, users, items


# ─────────────────────────────────────────────────────────────
# 3) 향상된 아이템 특성
# ─────────────────────────────────────────────────────────────
def extract_enhanced_item_features(
    df: pd.DataFrame,
    vod_mart_data: pd.DataFrame
) -> pd.DataFrame:
    """아이템-레벨 통계 + 시간/카테고리 패턴"""
    item_stats = df.groupby("asset_id").agg(
        total_views=("sha2_hash", "count"),
        unique_viewers=("sha2_hash", "nunique"),
        avg_completion=("completion_rate", "mean"),
        avg_watch_time=("use_tms", "mean"),
        popularity_score=("interaction_strength", "sum")
    ).reset_index()

    item_meta = vod_mart_data[
        ["asset_id", "genre", "category_l1", "category_l2", "super_asset_nm"]
    ].drop_duplicates("asset_id")

    item_features = item_stats.merge(item_meta, on="asset_id", how="left")

    # ─── 장르/카테고리 원-핫
    genre_dum = pd.get_dummies(item_features["genre"], prefix="genre")
    c1_dum    = pd.get_dummies(item_features["category_l1"], prefix="cat1")
    c2_dum    = pd.get_dummies(item_features["category_l2"], prefix="cat2")

    # ─── 시간대/요일 패턴
    hour_pat = df.groupby(["asset_id", "hour"])["interaction_strength"].sum().unstack(fill_value=0)
    hour_pat = hour_pat.div(hour_pat.sum(axis=1), axis=0).fillna(0)
    hour_pat.columns = [f"hour_{h}" for h in hour_pat.columns]

    wd_pat = df.groupby(["asset_id", "weekday_kr"])["interaction_strength"].sum().unstack(fill_value=0)
    wd_pat = wd_pat.div(wd_pat.sum(axis=1), axis=0).fillna(0)
    wd_pat.columns = [f"weekday_{d}" for d in wd_pat.columns]

    # ─── 결합
    item_features = item_features.set_index("asset_id")
    item_features = pd.concat(
        [item_features, genre_dum, c1_dum, c2_dum, hour_pat, wd_pat],
        axis=1
    ).fillna(0)
    # 불필요한 string 컬럼 drop
    item_features = item_features.drop(
        ["genre", "category_l1", "category_l2", "super_asset_nm"],
        axis=1, errors="ignore"
    )
    
        # ★★★ 여기부터 추가 / 변경 ★★★
    # index(=asset_id) 를 문자열로 통일하고 다시 컬럼으로 빼기
    item_features.index = item_features.index.astype(str)
    item_features = (
        item_features
        .reset_index()                # 새 컬럼 이름이 "index"
        .rename(columns={"index": "asset_id"})
    )

    # Parquet 로 나갈 object 컬럼은 전부 str 로 변환
    for col in item_features.select_dtypes(["object"]).columns:
        item_features[col] = item_features[col].astype(str)

    return item_features
