#!/usr/bin/env python
# 모델을 단 한 번만 학습하고 ./model/ 에 저장
import joblib, pandas as pd
from pathlib import Path
from utils import preprocess_data, train_optimized_als, extract_enhanced_item_features

# ─── 0) 경로 세팅
MODEL_DIR = Path("./model")
MODEL_DIR.mkdir(exist_ok=True)

# ─── 1) 데이터 로드
vod_mart = pd.read_csv("../data/processed/vod_mart_processed.csv")
combined = pd.read_csv("../data/processed/combined_df.csv").dropna(subset=["category"])


vod_mart["asset_id"]     = vod_mart["asset_id"].astype(str)
combined["asset_id"]     = combined["asset_id"].astype(str)
combined["sha2_hash"]    = combined["sha2_hash"].astype(str)

# ─── 2) 전처리
processed_df = preprocess_data(combined, vod_mart)
processed_df = processed_df.dropna(subset=["completion_rate"])

# ─── 3) ALS 학습
als_model, user2idx, item2idx, users, items = train_optimized_als(
    processed_df, factors=150, regularization=0.05, iterations=30
)

# ─── 4) 아이템 특성
item_features = extract_enhanced_item_features(processed_df, vod_mart)

# ─── 5) 저장
als_model.save(str(MODEL_DIR / "als_model.npz"))
joblib.dump(
    {
        "user2idx": user2idx,
        "item2idx": item2idx,
        "users"   : users,
        "items"   : items,
    },
    MODEL_DIR / "mappings.pkl"
)
item_features.to_parquet(MODEL_DIR / "item_features.parquet")

print("[INFO] Model artifacts saved in ./model/")
