#!/usr/bin/env python
# 저장된 모델을 메모리에 올려 추천을 수행
import os, joblib, numpy as np, pandas as pd
from implicit.cpu.als import AlternatingLeastSquares

class EnhancedHybridRecommender:
    # ──────────────────────────── 초기화 ────────────────────────────
    def __init__(
        self, *, als_model, user2idx, item2idx,
        processed_df, vod_mart_data, item_features,
        cf_weight=0.6, cb_weight=0.3, pop_weight=0.1,
        first_stage_size=500, diversity_factor=0.2
    ):
        # 파라미터
        total_w = cf_weight + cb_weight + pop_weight
        self.cf_weight = cf_weight / total_w
        self.cb_weight = cb_weight / total_w
        self.pop_weight = pop_weight / total_w
        self.first_stage_size = first_stage_size
        self.diversity_factor = diversity_factor

        # 데이터
        self.processed_df   = processed_df
        self.vod_mart_data  = vod_mart_data
        self.als_model      = als_model
        self.user2idx       = user2idx
        self.item2idx       = item2idx
        self.users          = np.array(list(user2idx.keys()))
        self.items          = np.array(list(item2idx.keys()))
        self.item_features  = item_features

        # 콘텐츠 행렬
        X = item_features.drop("asset_id", axis=1).astype(np.float64).to_numpy()
        norms = np.linalg.norm(X, axis=1)
        self.X_norm = X / np.maximum(norms[:, None], 1e-10)

        # 인기도 점수 정규화
        pop_raw = item_features.set_index("asset_id")["popularity_score"].fillna(0)
        max_pop = pop_raw.max() or 1.0
        self.popularity_scores = (pop_raw / max_pop).to_dict()

    # ──────────────────────────── 유틸 ────────────────────────────
    def get_user_profile(self, user_id, recency_weight=2.0):
        hist = self.processed_df[self.processed_df["sha2_hash"] == user_id]
        if hist.empty: return None

        if "use_dttm" in hist.columns:
            hist = hist.sort_values("use_dttm")

        n = len(hist)
        rec_w = np.power(np.linspace(1, recency_weight, n), 2)
        weights = hist["interaction_strength"].values * rec_w

        watched = hist["asset_id"].values
        idxs = [self.item2idx[it] for it in watched if it in self.item2idx]
        if not idxs: return None

        user_vec = weights @ self.X_norm[idxs]
        norm = np.linalg.norm(user_vec) or 1.0
        return user_vec / norm

    def compute_diversity_score(self, item_id, selected):
        if not selected: return 1.0
        idx = self.item2idx.get(item_id)
        if idx is None: return 0.0
        sel_idx = [self.item2idx[it] for it in selected if it in self.item2idx]
        if not sel_idx: return 1.0
        sims = self.X_norm[idx] @ self.X_norm[sel_idx].T
        return 1.0 - sims.mean()

    # ──────────────────────────── 추천 ────────────────────────────
    def recommend(self, user_id, N=10, exclude_seen=True):
        u_idx = self.user2idx.get(user_id)
        if u_idx is None:
            return self.recommend_popular(N)

        seen = set(self.processed_df.loc[
            self.processed_df["sha2_hash"] == user_id, "asset_id"
        ])
        candidates = [it for it in self.items if (not exclude_seen) or (it not in seen)]
        if not candidates:
            return self.recommend_popular(N)

        cidx = np.array([self.item2idx[it] for it in candidates])
        # CF
        cf_scores = self.als_model.item_factors[cidx] @ self.als_model.user_factors[u_idx]
        # 1차 상위
        K = min(self.first_stage_size, len(candidates))
        top_k_idx = np.argpartition(cf_scores, -K)[-K:]
        cf_top   = cf_scores[top_k_idx]
        cand_top = [candidates[i] for i in top_k_idx]
        cidx_top = cidx[top_k_idx]

        # CB
        user_prof = self.get_user_profile(user_id)
        if user_prof is None:
            return self.recommend_popular(N)
        cb_top = self.X_norm[cidx_top] @ user_prof

        # POP
        pop_top = np.array([self.popularity_scores.get(it, 0) for it in cand_top])

        # 정규화
        cf_n = cf_top / (cf_top.max() or 1.0)
        cb_n = cb_top / (cb_top.max() or 1.0)
        pop_n= pop_top/ (pop_top.max() or 1.0)
        base = (self.cf_weight*cf_n + self.cb_weight*cb_n + self.pop_weight*pop_n)

        # 다양성 고려 그리디
        selected=[]
        cand_pool=list(zip(cand_top, base))
        for _ in range(min(N, len(cand_pool))):
            div_scores=np.array([
                self.compute_diversity_score(it,[s[0] for s in selected])
                for it,_ in cand_pool
            ])
            comb = (1-self.diversity_factor)*np.array([b for _,b in cand_pool]) + \
                   self.diversity_factor*div_scores
            best = int(np.argmax(comb))
            selected.append(cand_pool.pop(best))
        return selected

    def recommend_popular(self, N=10):
        ranked = sorted(
            self.popularity_scores.items(), key=lambda x: x[1], reverse=True
        )
        return ranked[:N]

    def recommend_similar_to_item(self, item_id, N=10):
        if item_id not in self.item2idx: return []
        idx = self.item2idx[item_id]
        sims = self.X_norm @ self.X_norm[idx]
        sims[idx] = -1
        top = sims.argsort()[-N:][::-1]
        return [(self.items[i], sims[i]) for i in top]

    def explain_recommendation(self, user_id, rec_item):
        if user_id not in self.user2idx or rec_item not in self.item2idx:
            return "설명 불가"
        hist = self.processed_df[self.processed_df["sha2_hash"] == user_id]
        meta = self.vod_mart_data[self.vod_mart_data["asset_id"] == rec_item].iloc[0]
        genre_matches = hist[hist["genre"] == meta["genre"]]
        if not genre_matches.empty:
            ratio = genre_matches["asset_id"].nunique() / hist["asset_id"].nunique()
            if ratio > 0.3:
                return f"{meta['genre']} 장르를 즐겨 보셨기 때문입니다."
        sim_items = self.recommend_similar_to_item(rec_item, 3)
        if sim_items:
            sim_meta = self.vod_mart_data[
                self.vod_mart_data["asset_id"] == sim_items[0][0]
            ].iloc[0]
            return f"'{sim_meta['asset_nm']}' 과(와) 유사한 콘텐츠입니다."
        return "전반적인 시청 패턴과 유사합니다."

    # ──────────────────────────── 로더 ────────────────────────────
    @classmethod
    def load_from_disk(
        cls, model_dir, processed_df, vod_mart_data,
        cf_weight=0.6, cb_weight=0.3, pop_weight=0.1,
        first_stage_size=500, diversity_factor=0.2
    ):
        model_dir = os.fspath(model_dir)
        
        als = AlternatingLeastSquares.load(          # ← 클래스 메서드 호출
        os.path.join(model_dir, "als_model.npz")
    )

        maps = joblib.load(os.path.join(model_dir, "mappings.pkl"))
        item_feats = pd.read_parquet(os.path.join(model_dir, "item_features.parquet"))

        # ── NEW: 문자열 "True"/"False" → 1/0 변환 후 숫자형 강제 ──
        bool_map = {"True": 1, "False": 0, True: 1, False: 0}
        obj_cols  = item_feats.select_dtypes("object").columns.difference(["asset_id"])
        item_feats[obj_cols] = (
            item_feats[obj_cols]
            .replace(bool_map)                      # 1) bool 문자열 매핑
            .apply(pd.to_numeric, errors="coerce")  # 2) 숫자 아닌 값 → NaN
            .fillna(0)
            .astype(np.float32)
        )

        return cls(
            als_model=als,
            user2idx=maps["user2idx"],
            item2idx=maps["item2idx"],
            processed_df=processed_df,
            vod_mart_data=vod_mart_data,
            item_features=item_feats,
            cf_weight=cf_weight, cb_weight=cb_weight, pop_weight=pop_weight,
            first_stage_size=first_stage_size, diversity_factor=diversity_factor
        )
