import os
import time
import pandas as pd
import numpy as np
import scipy.sparse
import joblib
import sqlalchemy

from sklearn.feature_extraction.text import TfidfVectorizer
from implicit.als import AlternatingLeastSquares
from konlpy.tag import Okt

# 설정 파일에서 경로 상수 가져오기
from src.config import (
    DATA_PATH, CONTENT_DATA_PKL, ITEM_USER_NPZ, USER_ITEMS_NPZ,
    PREPROCESSED_DIR, TFIDF_MATRIX_NPZ, MAPS_PKL,
    ALS_DIR, TFIDF_DIR, DOCS_PATH, VEC_PATH, GV_PATH,
    DB_CONNECTION_STRING, MODEL_PKL
)

# ─────────────────────────────────────────────
# 0. 불용어 사전 로드
# ─────────────────────────────────────────────
STOPWORDS_PATH = "./stopwords-ko.txt"

def load_stopwords(path: str = STOPWORDS_PATH):
    """불용어 파일(한 줄당 단어 하나)을 읽어서 세트로 반환"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"불용어 파일을 찾을 수 없음: {path}")
    with open(path, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

stopwords = load_stopwords()
print(f"✅ 불용어 {len(stopwords):,}개 로드 완료")

# ─────────────────────────────────────────────
# 1. 형태소 분석기 (Okt)
# ─────────────────────────────────────────────
okt = Okt()

def analyze_text(text: str) -> str:
    """Okt로 명사, 동사, 형용사를 추출해 공백으로 구분된 문자열 반환"""
    if pd.isna(text) or not text:
        return ""
    return " ".join(
        word for word, pos in okt.pos(text, stem=True)
        if pos in {"Noun", "Verb", "Adjective"} and len(word) > 1 and word not in stopwords
    )

# ─────────────────────────────────────────────
# 2. 콘텐츠 문서 생성
# ─────────────────────────────────────────────

def build_document(row: pd.Series) -> str:
    """줄거리, 장르, 배우 정보를 조합해 텍스트 문서 생성"""
    genre_text = ((row.get("genre") + " ") * 3).strip() if pd.notna(row.get("genre")) else ""
    smry_analyzed = analyze_text(row.get("smry", "") or "")
    actor_text = row.get("actr_disp", "") if pd.notna(row.get("actr_disp")) else ""
    return " ".join(filter(None, [smry_analyzed, genre_text, actor_text]))

# ─────────────────────────────────────────────
# 3. 그룹핑·메모리 최적화 도우미
# ─────────────────────────────────────────────

def group_content(df_: pd.DataFrame):
    """콘텐츠를 super_asset_nm과 smry로 그룹화하고 group_id 할당"""
    grp = df_.groupby(["super_asset_nm", "smry"], as_index=False)["asset_id"].apply(list)
    grp["group_id"] = range(len(grp))
    id2grp = {aid: gid for _, (assets, gid) in grp[["asset_id", "group_id"]].iterrows() for aid in assets}
    df_ = df_.copy()
    df_["group_id"] = df_["asset_id"].map(id2grp)
    return df_, grp

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임 메모리 사용량 최적화"""
    int_cols = ["user_index", "u_idx", "i_idx", "group_id"]
    for col in int_cols:
        if col in df:
            df[col] = pd.to_numeric(df[col], downcast="integer", errors="coerce")
    if "weight" in df:
        df["weight"] = pd.to_numeric(df["weight"], downcast="float", errors="coerce")
    cat_cols = ["super_asset_nm", "smry", "genre", "actr_disp", "poster_url", "orgnl_cntry"]
    for col in cat_cols:
        if col in df:
            df[col] = df[col].astype("category")
    return df

# ─────────────────────────────────────────────
# 4. 형태소 분석 (체크포인트)
# ─────────────────────────────────────────────

def generate_analyzed_texts(content_df: pd.DataFrame):
    """Okt로 형태소 분석 후 체크포인트 저장"""
    analyzed_texts = joblib.load(DOCS_PATH) if os.path.exists(DOCS_PATH) else {}
    pending_df = content_df[~content_df["group_id"].isin(analyzed_texts.keys())]
    if pending_df.empty:
        print(f"🔄 형태소 분석 스킵 (이미 {len(analyzed_texts)}개 그룹 완료)")
        return analyzed_texts
    print(f"🔍 형태소 분석 진행 중… (새 {len(pending_df)}개)")
    start = time.time()
    for _, row in pending_df.iterrows():
        analyzed_texts[row["group_id"]] = build_document(row)
    joblib.dump(analyzed_texts, DOCS_PATH)
    print(f"✅ 형태소 분석 누적 저장 ({len(analyzed_texts)}개, {time.time()-start:.1f}s) → {DOCS_PATH}")
    return analyzed_texts

# ─────────────────────────────────────────────
# 5. TF‑IDF 벡터화
# ─────────────────────────────────────────────

def generate_tfidf_vectors(text_data: dict):
    """텍스트 데이터를 TF-IDF 벡터로 변환"""
    tfidf = TfidfVectorizer(
        min_df=3, max_df=0.9,
        max_features=5000,
        ngram_range=(1, 2),
        norm="l2", use_idf=True, smooth_idf=True
    )
    print("🔍 TF‑IDF 벡터화…")
    matrix = tfidf.fit_transform(list(text_data.values()))
    vectors = {gid: matrix[idx] for idx, gid in enumerate(text_data.keys())}
    print(f"✅ TF‑IDF 완료 {matrix.shape}")
    return tfidf, vectors, matrix

# ─────────────────────────────────────────────
# 6. ALS 학습
# ─────────────────────────────────────────────

def train_als_model(item_user, factors=100, iterations=50):
    """ALS 모델 학습"""
    model = AlternatingLeastSquares(
        factors=factors,
        regularization=0.1,
        iterations=iterations,
        calculate_training_loss=True,
        use_gpu=False
    )
    print(f"🤖 ALS 학습 시작 (f={factors}, it={iterations})…")
    model.fit(item_user.T, show_progress=True)
    print("✅ ALS 학습 완료")
    return model

# ─────────────────────────────────────────────
# 7. 사용자 입력 처리
# ─────────────────────────────────────────────

def input_yn(prompt: str) -> bool:
    """Y/N 입력을 받아 대소문자 구분 없이 처리"""
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("잘못된 입력입니다. Y 또는 N을 입력해주세요.")

# ─────────────────────────────────────────────
# 8. 메인 파이프라인
# ─────────────────────────────────────────────

def preprocess_and_save():
    print("🚀 하이브리드 추천 전처리 시작…")
    # 디렉터리 생성
    os.makedirs(PREPROCESSED_DIR, exist_ok=True)
    os.makedirs(ALS_DIR, exist_ok=True)
    os.makedirs(TFIDF_DIR, exist_ok=True)
    # 1) 데이터 로드
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없음: {DATA_PATH}")
    cols = ["user_index", "asset_id", "weight", "super_asset_nm", "smry", "genre", "actr_disp", "poster_url", "orgnl_cntry"]
    df = pd.read_parquet(DATA_PATH, columns=cols)
    print(f"✅ 데이터 로드 ({len(df):,} 행)")
    print(f"df 컬럼: {list(df.columns)}")
    
    # 2) 사용자/아이템 매핑
    user_map = {u: i for i, u in enumerate(df["user_index"].unique())}
    item_map = {a: i for i, a in enumerate(df["asset_id"].unique())}
    df = df[df["user_index"].isin(user_map) & df["asset_id"].isin(item_map)].copy()
    df["u_idx"] = df["user_index"].map(user_map)
    df["i_idx"] = df["asset_id"].map(item_map)
    print(f"✅ 매핑 완료 (users={len(user_map):,}, items={len(item_map):,})")
    
    # 3) 희소 행렬 생성
    item_user = scipy.sparse.coo_matrix(
    (df["weight"].astype(np.float32), (df["i_idx"], df["u_idx"])),
    shape=(len(item_map), len(user_map)),
    dtype=np.float32
    ).tocsr()
    user_items = item_user.T.tocsr()
    scipy.sparse.save_npz(ITEM_USER_NPZ, item_user)
    scipy.sparse.save_npz(USER_ITEMS_NPZ, user_items)
    print(f"✅ 희소 행렬 저장 (item_user: {item_user.shape}, user_items: {user_items.shape})")
    
    # 4) 콘텐츠 전처리 & 그룹핑
    content_df = df[["asset_id", "super_asset_nm", "smry", "genre", "actr_disp", "poster_url", "orgnl_cntry"]].drop_duplicates(subset="asset_id")
    content_df, grp_meta = group_content(content_df)
    asset_to_group = content_df.set_index("asset_id")["group_id"].to_dict()
    # 대표 매핑 생성
    rep_map = {row["group_id"]: row["asset_id"][0] for _, row in grp_meta.iterrows()}
    joblib.dump({
        "content_df": content_df,
        "grp_meta": grp_meta,
        "asset_to_group": asset_to_group,
        "rep_map": rep_map
    }, CONTENT_DATA_PKL, compress=3)
    print(f"✅ 콘텐츠 데이터 저장 → {CONTENT_DATA_PKL}")
    print(f"content_df 컬럼: {list(content_df.columns)}")
    # 4.1) df에 group_id 추가
    df["group_id"] = df["asset_id"].map(asset_to_group)
    print(f"✅ df에 group_id 추가 (결측치: {df['group_id'].isna().sum()})")
    print(f"df 컬럼: {list(df.columns)}")
    # 5) 형태소 분석
    analyzed_texts = generate_analyzed_texts(content_df)
    # 6) TF‑IDF
    if not (os.path.exists(VEC_PATH) and os.path.exists(GV_PATH)):
        tfidf, group_vectors, matrix = generate_tfidf_vectors(analyzed_texts)
        joblib.dump(tfidf, VEC_PATH)
        joblib.dump(group_vectors, GV_PATH)
        for i in range(0, matrix.shape[0], 10000):
            scipy.sparse.save_npz(os.path.join(TFIDF_DIR, f"tfidf_part_{i}.npz"), matrix[i:i+10000])
        print("✅ TF-IDF 저장 완료")
    else:
        tfidf = joblib.load(VEC_PATH)
        group_vectors = joblib.load(GV_PATH)
        print("🔄 TF-IDF 로드 완료")
    # 7) ALS 학습
    if not os.path.exists(MODEL_PKL):
        als_model = train_als_model(item_user)
        payload = {
            "model": als_model,
            "user_map": user_map,
            "item_map": item_map,
            "bucket_bins": [0, 0.25, 0.5, 0.75, 1.0]
        }
        joblib.dump(payload, MODEL_PKL)
        print(f"✅ ALS 모델 저장 → {MODEL_PKL}")
    else:
        print("🔄 ALS 모델 이미 존재")
    # 8) 사용자 선호·매핑 생성
    user_watched = df.groupby("user_index")["asset_id"].agg(list).to_dict()
    user_groups = df.groupby("user_index")["group_id"].agg(lambda x: list(set(x))).to_dict()
    user_watched_programs = df.groupby("user_index")["super_asset_nm"].agg(lambda x: list(set(x))).to_dict()
    genre_counts = df.groupby(["user_index", "genre"]).size().reset_index(name="count")
    user_genre_pref = genre_counts.groupby("user_index")[["genre", "count"]].apply(
        lambda x: dict(zip(x["genre"], x["count"] / x["count"].sum()))
    ).to_dict()
    country_counts = df.groupby(["user_index", "orgnl_cntry"]).size().reset_index(name="count")
    user_country_pref = country_counts.groupby("user_index")[["orgnl_cntry", "count"]].apply(
        lambda x: dict(zip(x["orgnl_cntry"], x["count"] / x["count"].sum()))
    ).to_dict()
    asset_to_genre = content_df.set_index("asset_id")["genre"].to_dict()
    asset_to_country = content_df.set_index("asset_id")["orgnl_cntry"].to_dict()
    asset_to_poster = content_df.set_index("asset_id")["poster_url"].to_dict()
    maps = {
        "user_watched": user_watched,
        "user_groups": user_groups,
        "user_watched_programs": user_watched_programs,
        "user_genre_pref": user_genre_pref,
        "user_country_pref": user_country_pref,
        "asset_to_genre": asset_to_genre,
        "asset_to_country": asset_to_country,
        "asset_to_poster": asset_to_poster
    }
    joblib.dump(maps, MAPS_PKL, compress=3)
    print(f"✅ 사용자 선호 매핑 저장 → {MAPS_PKL}")
    # 9) DB 저장 (선택적)
    if input_yn("DB에 데이터를 업로드하시겠습니까? (Y/N): "):
        print("=== DB 업로드 시작")
        df = optimize_dataframe(df)
        engine = sqlalchemy.create_engine(DB_CONNECTION_STRING)
        df.to_sql("filtered_data", engine, if_exists="replace", index=False)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("CREATE INDEX IF NOT EXISTS idx_user_index ON filtered_data (user_index)"))
            conn.execute(sqlalchemy.text("CREATE INDEX IF NOT EXISTS idx_asset_id ON filtered_data (asset_id)"))
            conn.execute(sqlalchemy.text("CREATE INDEX IF NOT EXISTS idx_group_id ON filtered_data (group_id)"))
            conn.commit()
        print("✅ DB 업로드 완료")
    else:
        print("🔄 DB 업로드 스킵 (기존 데이터 유지)")
    print("🎉 전처리 파이프라인 완료")

# ─────────────────────────────────────────────
# 9. 실행 진입점
# ─────────────────────────────────────────────
if __name__ == "__main__":
    preprocess_and_save()