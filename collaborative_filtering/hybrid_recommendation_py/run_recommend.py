#!/usr/bin/env python
# 모델이 없으면 자동으로 train_and_save.py 실행 후 추천
import os, subprocess, pandas as pd
from pathlib import Path
from utils import preprocess_data
from recommender import EnhancedHybridRecommender

MODEL_DIR = Path("./model")
DATA_DIR  = Path("../data/processed")

# 1) 모델 없으면 학습
if not MODEL_DIR.exists():
    print("[INFO] model/ not found → start training …")
    subprocess.check_call(["python", "train_and_save.py"])

# 2) 데이터 로드 & 전처리 (추천 시 필요한 최소 정보)
vod_mart = pd.read_csv(DATA_DIR / "vod_mart_processed.csv")
combined = pd.read_csv(DATA_DIR / "combined_df.csv").dropna(subset=["category"])
processed_df = preprocess_data(combined, vod_mart).dropna(subset=["completion_rate"])

# 3) 모델 불러오기
rec = EnhancedHybridRecommender.load_from_disk(
    MODEL_DIR, processed_df, vod_mart,
    cf_weight=0.6, cb_weight=0.3, pop_weight=0.1, diversity_factor=0.2
)

# 4) 사용자 입력 → 추천
user_id = input("SHA2 hash 입력 ▶ ").strip()
results = rec.recommend(user_id, N=10)

print(f"\n[추천 결과] 사용자 {user_id[:8]}…")
for i, (aid, score) in enumerate(results, 1):
    meta = vod_mart.loc[vod_mart["asset_id"] == aid].iloc[0]
    print(f"{i:02d}. {meta['super_asset_nm'][:50]}…  (점수 {score:.3f})")
    # print("   이유:", rec.explain_recommendation(user_id, aid))
