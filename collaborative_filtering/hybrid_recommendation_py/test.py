import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
from sklearn.model_selection import train_test_split
from surprise import Reader, Dataset
from sklearn.metrics import precision_score, recall_score, ndcg_score

# 데이터 전처리 함수는 그대로 유지
def preprocess_data(df, vod_data):
    # 필요한 컬럼만 선택
    df = df.merge(
        vod_data[['asset_id', 'genre', 'category_l1', 'category_l2', 'super_asset_nm']],
        on='asset_id',
        how='left'
    )
    
    # 시청 완료율 계산
    df['completion_rate'] = df['use_tms'] / df['disp_rtm']
    df['completion_rate'] = df['completion_rate'].clip(0, 1)
    
    # 시청 시간 정규화
    scaler = MinMaxScaler()
    df['normalized_time'] = scaler.fit_transform(df[['use_tms']])
    
    # 중요: 상호작용 강도 점수 계산 추가
    # 시청 완료율과 정규화된 시간을 결합하여 상호작용 강도 계산
    df['interaction_strength'] = 0.7 * df['completion_rate'] + 0.3 * df['normalized_time']
    
    return df

# ALS 모델 개선을 위한 함수
def train_optimized_als(processed_df, factors=150, regularization=0.05, iterations=30):
    """개선된 ALS 모델 학습 함수"""
    # 인덱스 맵핑
    users, user_idx = np.unique(processed_df['sha2_hash'], return_inverse=True)
    items, item_idx = np.unique(processed_df['asset_id'], return_inverse=True)
    
    # 상호작용 강도를 사용하여 희소행렬 생성
    data = processed_df['interaction_strength'].values
    mat = coo_matrix((data, (item_idx, user_idx)))
    
    # 개선된 ALS 모델 초기화 & 학습
    als_model = AlternatingLeastSquares(
        factors=factors, 
        regularization=regularization, 
        iterations=iterations, 
        calculate_training_loss=True,
        use_gpu=False
    )
    als_model.fit(mat)
    
    # 인덱스 맵핑 dict 생성
    user2idx = {u:i for i,u in enumerate(users)}
    item2idx = {item: idx for idx, item in enumerate(items)}
    
    return als_model, user2idx, item2idx, users, items

# 개선된 사용자 특성 추출 함수
def extract_enhanced_user_features(df):
    """보다 세밀한 사용자 특성 추출 함수"""
    # 1) 기본 통계 - 시청 강도(recency, frequency, monetary) 고려
    # 최신성, 빈도, 시청시간을 함께 고려
    user_features = df.groupby('sha2_hash').agg(
        total_sessions=('asset_id', 'count'),
        avg_watch_time=('use_tms', 'mean'),
        avg_completion_rate=('completion_rate', 'mean'),
        unique_contents=('asset_id', 'nunique'),
        total_watch_time=('use_tms', 'sum'),  # 총 시청시간 추가
        max_completion_rate=('completion_rate', 'max')  # 최대 완료율 추가
    ).reset_index()
    
    # 2) 선호 장르 - 시청 완료율로 가중치 적용
    genre_weights = df.groupby(['sha2_hash', 'genre'])['interaction_strength'].sum().reset_index()
    genre_pivot = genre_weights.pivot(index='sha2_hash', columns='genre', values='interaction_strength').fillna(0)
    genre_pivot.columns = [f'genre_{col}' for col in genre_pivot.columns]
    
    # 3) 카테고리 선호도 - L1, L2 카테고리별 선호도
    cat_l1_weights = df.groupby(['sha2_hash', 'category_l1'])['interaction_strength'].sum().reset_index()
    cat_l1_pivot = cat_l1_weights.pivot(index='sha2_hash', columns='category_l1', values='interaction_strength').fillna(0)
    cat_l1_pivot.columns = [f'cat1_{col}' for col in cat_l1_pivot.columns]
    
    cat_l2_weights = df.groupby(['sha2_hash', 'category_l2'])['interaction_strength'].sum().reset_index()
    cat_l2_pivot = cat_l2_weights.pivot(index='sha2_hash', columns='category_l2', values='interaction_strength').fillna(0)
    cat_l2_pivot.columns = [f'cat2_{col}' for col in cat_l2_pivot.columns]
    
    # 4) 시간대별 시청 패턴 - 가중치 적용
    hour_weights = df.groupby(['sha2_hash', 'hour'])['interaction_strength'].sum().reset_index()
    hour_pivot = hour_weights.pivot(index='sha2_hash', columns='hour', values='interaction_strength').fillna(0)
    hour_pivot.columns = [f'hour_{col}' for col in hour_pivot.columns]
    
    # 5) 요일별 시청 패턴 - 가중치 적용
    weekday_weights = df.groupby(['sha2_hash', 'weekday_kr'])['interaction_strength'].sum().reset_index()
    weekday_pivot = weekday_weights.pivot(index='sha2_hash', columns='weekday_kr', values='interaction_strength').fillna(0)
    weekday_pivot.columns = [f'weekday_{col}' for col in weekday_pivot.columns]
    
    # 6) 모든 특성 결합
    # 각 피벗 테이블에 인덱스가 없는 경우 대비
    for pivot in [genre_pivot, cat_l1_pivot, cat_l2_pivot, hour_pivot, weekday_pivot]:
        if pivot.empty:
            continue
    
    dfs_to_merge = [df for df in [genre_pivot, cat_l1_pivot, cat_l2_pivot, hour_pivot, weekday_pivot] if not df.empty]
    
    # 모든 피벗 테이블을 결합
    user_features = user_features.set_index('sha2_hash')
    for pivot_df in dfs_to_merge:
        user_features = user_features.join(pivot_df, how='left')
    
    # 결측치 처리
    user_features = user_features.fillna(0).reset_index()
    
    return user_features

# 개선된 아이템 특성 추출 함수
def extract_enhanced_item_features(df, vod_mart_data):
    """보다 세밀한 아이템 특성 추출 함수"""
    # 1) 기본 콘텐츠 통계
    item_features = df.groupby('asset_id').agg(
        total_views=('sha2_hash', 'count'),
        unique_viewers=('sha2_hash', 'nunique'),
        avg_completion=('completion_rate', 'mean'),
        avg_watch_time=('use_tms', 'mean'),
        popularity_score=('interaction_strength', 'sum')  # 인기도 점수 추가
    ).reset_index()
    
    # vod_mart_data에서 추가 메타데이터 병합
    item_meta = vod_mart_data[['asset_id', 'genre', 'category_l1', 'category_l2', 'super_asset_nm']].drop_duplicates('asset_id')
    item_features = item_features.merge(item_meta, on='asset_id', how='left')
    
    # 2) 장르 및 카테고리 원핫 인코딩
    genre_dummies = pd.get_dummies(item_features['genre'], prefix='genre')
    cat1_dummies = pd.get_dummies(item_features['category_l1'], prefix='cat1')
    cat2_dummies = pd.get_dummies(item_features['category_l2'], prefix='cat2')
    
    # 3) 시간대별 시청 패턴 - 정규화된 가중치 적용
    hour_patterns = df.groupby(['asset_id', 'hour'])['interaction_strength'].sum().reset_index()
    hour_patterns_pivot = hour_patterns.pivot(index='asset_id', columns='hour', values='interaction_strength').fillna(0)
    # 각 행을 합계로 나눠 정규화
    hour_sums = hour_patterns_pivot.sum(axis=1)
    hour_patterns_norm = hour_patterns_pivot.div(hour_sums, axis=0).fillna(0)
    hour_patterns_norm.columns = [f'hour_{col}' for col in hour_patterns_norm.columns]
    
    # 4) 요일별 시청 패턴 - 정규화된 가중치 적용
    weekday_patterns = df.groupby(['asset_id', 'weekday_kr'])['interaction_strength'].sum().reset_index()
    weekday_patterns_pivot = weekday_patterns.pivot(index='asset_id', columns='weekday_kr', values='interaction_strength').fillna(0)
    # 각 행을 합계로 나눠 정규화
    weekday_sums = weekday_patterns_pivot.sum(axis=1)
    weekday_patterns_norm = weekday_patterns_pivot.div(weekday_sums, axis=0).fillna(0)
    weekday_patterns_norm.columns = [f'weekday_{col}' for col in weekday_patterns_norm.columns]
    
    # 5) 모든 특성 결합
    item_features = item_features.set_index('asset_id')
    features_combined = pd.concat([
        item_features,
        genre_dummies,
        cat1_dummies, 
        cat2_dummies,
        hour_patterns_norm,
        weekday_patterns_norm
    ], axis=1)
    
    # 특성에서 원본 카테고리 컬럼 제거
    features_combined = features_combined.drop(['genre', 'category_l1', 'category_l2', 'super_asset_nm'], axis=1, errors='ignore')
    
    return features_combined.reset_index()

# 개선된 하이브리드 추천 시스템
class EnhancedHybridRecommender:
    def __init__(self, processed_df, vod_mart_data, als_factors=150, als_reg=0.05, 
                 cf_weight=0.6, cb_weight=0.3, pop_weight=0.1, 
                 first_stage_size=500, diversity_factor=0.2):
        """
        개선된 하이브리드 추천 시스템
        
        Parameters:
        -----------
        processed_df : DataFrame
            전처리된 사용자 행동 데이터
        vod_mart_data : DataFrame
            VOD 메타데이터
        als_factors : int
            ALS 모델의 잠재 요인 수
        als_reg : float
            ALS 모델의 정규화 파라미터
        cf_weight : float
            협업 필터링 가중치
        cb_weight : float 
            콘텐츠 기반 필터링 가중치
        pop_weight : float
            인기도 기반 필터링 가중치
        first_stage_size : int
            1차 후보 선정 크기
        diversity_factor : float
            다양성 조절 계수 (0에 가까울수록 유사 콘텐츠 우선, 1에 가까울수록 다양성 우선)
        """
        self.processed_df = processed_df
        self.vod_mart_data = vod_mart_data
        self.cf_weight = cf_weight
        self.cb_weight = cb_weight
        self.pop_weight = pop_weight
        self.first_stage_size = first_stage_size
        self.diversity_factor = diversity_factor
        
        # 전체 가중치 합이 1이 되도록 정규화
        total_weight = cf_weight + cb_weight + pop_weight
        self.cf_weight /= total_weight
        self.cb_weight /= total_weight
        self.pop_weight /= total_weight
        
        # ALS 모델 학습
        self.als_model, self.user2idx, self.item2idx, self.users, self.items = train_optimized_als(
            processed_df, factors=als_factors, regularization=als_reg
        )
        
        # 아이템 특성 추출
        self.item_features = extract_enhanced_item_features(processed_df, vod_mart_data)
        
        # 콘텐츠 기반 필터링을 위한 특성 행렬 준비
        self.X = self.item_features.drop('asset_id', axis=1).astype(np.float64).to_numpy()
        self.norms = np.linalg.norm(self.X, axis=1)
        self.X_norm = self.X / np.maximum(self.norms[:, None], 1e-10)  # 0으로 나누는 것 방지
        
        # 인기도 점수 계산 및 정규화
        self.popularity_scores = {}
        for idx, row in self.item_features.iterrows():
            self.popularity_scores[row['asset_id']] = row.get('popularity_score', 0)
        
        max_pop = max(self.popularity_scores.values()) if self.popularity_scores else 1
        for k in self.popularity_scores:
            self.popularity_scores[k] /= max_pop
    
    def get_user_profile(self, user_id, recency_weight=2.0):
        """사용자 프로필 벡터 계산 - 최신 시청 콘텐츠에 더 높은 가중치 부여"""
        # 사용자의 시청 기록 가져오기
        user_history = self.processed_df[self.processed_df['sha2_hash'] == user_id]
        
        if user_history.empty:
            return None
        
        # 시청 시간 기준으로 정렬
        if 'use_dttm' in user_history.columns:
            user_history = user_history.sort_values('use_dttm')
        
        # 최신 시청에 더 높은 가중치 부여
        n_items = len(user_history)
        recency_weights = np.power(np.linspace(1, recency_weight, n_items), 2)
        
        # 상호작용 강도와 최신성 결합
        weights = user_history['interaction_strength'].values * recency_weights
        
        # 시청한 콘텐츠 가져오기
        watched_items = user_history['asset_id'].values
        widxs = np.array([self.item2idx.get(it, 0) for it in watched_items if it in self.item2idx])
        
        if len(widxs) == 0:
            return None
            
        # 사용자 프로필 계산
        W = self.X[widxs]  # (n_watched, n_feats)
        user_prof = (weights.reshape(1,-1) @ W).flatten()  # (n_feats,)
        up_norm = np.linalg.norm(user_prof) or 1.0
        user_prof /= up_norm  # 단위 벡터화
        
        return user_prof
    
    def compute_diversity_score(self, item_id, selected_items):
        """이미 선택된 아이템들과의 다양성 점수 계산"""
        if not selected_items:
            return 1.0  # 첫 아이템은 다양성 최대
            
        item_idx = self.item2idx.get(item_id)
        if item_idx is None:
            return 0.0
            
        selected_idxs = [self.item2idx.get(it) for it in selected_items if it in self.item2idx]
        if not selected_idxs:
            return 1.0
            
        # 선택된 아이템들과의 평균 유사도 계산
        similarities = []
        for sel_idx in selected_idxs:
            sim = np.dot(self.X_norm[item_idx], self.X_norm[sel_idx])
            similarities.append(sim)
            
        avg_sim = np.mean(similarities)
        # 다양성 점수 = 1 - 유사도 (유사도가 낮을수록 다양성 높음)
        return 1.0 - avg_sim
    
    def recommend(self, user_id, N=10, exclude_seen=True, max_history_items=20):
        """개선된 추천 알고리즘"""
        # 1) 사용자 인덱스
        u = self.user2idx.get(user_id)
        if u is None:
            # 콜드 스타트 사용자 처리: 인기도 기반 추천 
            return self.recommend_popular(N)
        
        # 2) 후보 아이템 + 인덱스
        seen = set(self.processed_df.loc[self.processed_df['sha2_hash']==user_id, 'asset_id'])
        candidates = [it for it in self.items if (not exclude_seen) or (it not in seen)]
        cidx_all = np.array([self.item2idx.get(it, 0) for it in candidates if it in self.item2idx])
        
        if len(cidx_all) == 0:
            return self.recommend_popular(N)
        
        # 3) CF 점수 전체 계산
        user_vec = self.als_model.user_factors[u]  # (factors,)
        cf_scores_all = self.als_model.item_factors[cidx_all] @ user_vec  # (n_cand,)
        
        # 4) 1차 랭킹: CF 기준 상위 K1
        K1 = min(self.first_stage_size, len(cidx_all))
        idx1 = np.argpartition(cf_scores_all, -K1)[-K1:]  # CF 점수 상위 K1(unsorted)
        cidx1 = cidx_all[idx1]
        cand1 = [candidates[i] for i in idx1]
        cf1 = cf_scores_all[idx1]
        
        # 5) 사용자 프로파일 벡터 (가중합)
        user_prof = self.get_user_profile(user_id)
        if user_prof is None:
            # 프로필 생성 실패 시 인기도 기반 추천
            return self.recommend_popular(N)
        
        # 6) CB 점수 (1차 후보만) 
        cb1 = self.X_norm[cidx1] @ user_prof  # (K1,)
        
        # 7) 인기도 점수 추가
        pop1 = np.array([self.popularity_scores.get(it, 0) for it in cand1])
        
        # 8) 정규화 & 가중합
        cf_n = cf1 / (np.max(cf1) or 1)
        cb_n = cb1 / (np.max(cb1) or 1)
        pop_n = pop1 / (np.max(pop1) or 1)
        
        # 기본 점수 계산
        base_scores = (self.cf_weight * cf_n + 
                       self.cb_weight * cb_n + 
                       self.pop_weight * pop_n)
                       
        # 9) 다양성을 고려한 최종 추천
        final_recommendations = []
        remaining_candidates = list(zip(cand1, base_scores))
        
        # 그리디 알고리즘으로 다양성 고려한 추천
        for _ in range(min(N, len(remaining_candidates))):
            if not remaining_candidates:
                break
                
            # 다양성 점수 계산
            diversity_scores = np.array([
                self.compute_diversity_score(cand, [r[0] for r in final_recommendations]) 
                for cand, _ in remaining_candidates
            ])
            
            # 기본 점수와 다양성 점수 결합
            combined_scores = np.array([score for _, score in remaining_candidates]) * (1 - self.diversity_factor) + \
                              diversity_scores * self.diversity_factor
                              
            # 최고 점수 아이템 선택
            best_idx = np.argmax(combined_scores)
            final_recommendations.append(remaining_candidates[best_idx])
            
            # 선택된 아이템 제거
            remaining_candidates.pop(best_idx)
        
        return final_recommendations
        
    def recommend_popular(self, N=10):
        """인기도 기반 추천 (콜드 스타트 문제 해결)"""
        items_by_pop = sorted(self.popularity_scores.items(), key=lambda x: x[1], reverse=True)
        return [(item_id, score) for item_id, score in items_by_pop[:N]]
        
    def recommend_similar_to_item(self, item_id, N=10):
        """특정 아이템과 유사한 아이템 추천"""
        if item_id not in self.item2idx:
            return []
            
        item_idx = self.item2idx[item_id]
        item_vector = self.X_norm[item_idx]
        
        # 모든 아이템과의 유사도 계산
        similarities = self.X_norm @ item_vector
        
        # 자기 자신 제외
        similarities[item_idx] = -1
        
        # 상위 N개 유사 아이템 반환
        top_indices = np.argsort(similarities)[-N:][::-1]
        return [(self.items[idx], similarities[idx]) for idx in top_indices]

    def explain_recommendation(self, user_id, rec_item_id):
        """추천 결과 설명"""
        if user_id not in self.user2idx or rec_item_id not in self.item2idx:
            return "추천 설명을 생성할 수 없습니다."
            
        # 1. 사용자가 시청한 콘텐츠
        user_history = self.processed_df[self.processed_df['sha2_hash'] == user_id]
        watched_items = user_history['asset_id'].unique()
        
        # 2. 추천 아이템 정보
        rec_info = self.vod_mart_data[self.vod_mart_data['asset_id'] == rec_item_id].iloc[0]
        
        # 3. 장르 기반 설명
        genre_matches = user_history[user_history['genre'] == rec_info['genre']]
        genre_explanation = ""
        if not genre_matches.empty:
            watched_genre = genre_matches['asset_id'].nunique()
            total_watched = len(watched_items)
            genre_ratio = watched_genre / total_watched
            if genre_ratio > 0.3:
                genre_explanation = f"사용자가 주로 시청한 {rec_info['genre']} 장르와 일치합니다."
            else:
                similar_items = self.recommend_similar_to_item(rec_item_id, 3)
                if similar_items:
                    similar_info = [self.vod_mart_data[self.vod_mart_data['asset_id'] == i[0]].iloc[0]['asset_nm'] 
                                   for i in similar_items if i[0] in self.vod_mart_data['asset_id'].values]
                    if similar_info:
                        genre_explanation = f"사용자가 시청한 '{similar_info[0]}' 등의 콘텐츠와 유사합니다."
        
        return genre_explanation if genre_explanation else "사용자의 전반적인 시청 패턴과 일치합니다."

# 추천 결과 생성 및 평가 함수
def evaluate_enhanced_recommendations(recommender, user_id, vod_mart_data, n=10):
    """개선된 추천 결과 생성 및 평가"""
    # 추천 결과 가져오기
    recommendations = recommender.recommend(user_id, N=n)
    
    print(f"=== 사용자 {user_id[:8]}... 에 대한 추천 결과 ===")
    
    # 사용자 시청 이력
    user_history = recommender.processed_df[recommender.processed_df['sha2_hash'] == user_id]
    top_genres = user_history['genre'].value_counts().head(3)
    print(f"사용자 주요 시청 장르: {', '.join(top_genres.index)}")
    
    for item_id, score in recommendations:
        # vod_mart_data에서 asset_id로 메타정보 조회
        content_info = vod_mart_data.loc[
            vod_mart_data['asset_id'] == item_id
        ]
        
        if content_info.empty:
            continue
            
        content_info = content_info.iloc[0]
        
        print(f"제목: {content_info['asset_nm'][:50]}...")
        print(f"장르: {content_info['genre']}")
        print(f"카테고리: {content_info['category_l1']} > {content_info['category_l2']}")
        print(f"추천 점수: {score:.3f}")
        
        # 추천 이유 설명
        explanation = recommender.explain_recommendation(user_id, item_id)
        print(f"추천 이유: {explanation}\n")

# 모델 사용 예시
def main():
    # 데이터 로드
    vod_mart_data = pd.read_csv('../data/processed/vod_mart_processed.csv')
    combined_data = pd.read_csv('../data/processed/combined_df.csv')
    combined_data.dropna(subset=['category'], inplace=True)
    
    # 데이터 전처리
    processed_df = preprocess_data(combined_data, vod_mart_data)
    processed_df.dropna(subset=['completion_rate'], inplace=True)
    
    # 하이브리드 추천 시스템 초기화
    recommender = EnhancedHybridRecommender(
        processed_df=processed_df,
        vod_mart_data=vod_mart_data,
        als_factors=150,
        als_reg=0.05,
        cf_weight=0.6,
        cb_weight=0.3,
        pop_weight=0.1,
        diversity_factor=0.2
    )
    
    # 샘플 사용자에 대한 추천 생성
    sample_user = processed_df['sha2_hash'].iloc[0]
    evaluate_enhanced_recommendations(recommender, sample_user, vod_mart_data, n=10)

if __name__ == "__main__":
    main()