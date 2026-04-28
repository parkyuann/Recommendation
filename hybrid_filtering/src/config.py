import os

BASE_DIR = "./"
ALS_DIR = os.path.join(BASE_DIR, "files/ALS")
TFIDF_DIR = os.path.join(BASE_DIR, "files/TF-IDF")
PREPROCESSED_DIR = os.path.join(BASE_DIR, "files/preprocessed")

MODEL_PKL = os.path.join(ALS_DIR, "als_full.pkl")

DOCS_PATH = os.path.join(TFIDF_DIR, "analyzed_texts.pkl")
VEC_PATH = os.path.join(TFIDF_DIR, "tfidf_vectorizer.pkl")
GV_PATH = os.path.join(TFIDF_DIR, "group_vectors.pkl")

DATA_PATH = os.path.join(BASE_DIR, "data/hybrid_rec_data_final_v2.parquet")

CONTENT_DATA_PKL = os.path.join(PREPROCESSED_DIR, "content_data.pkl")
ITEM_USER_NPZ = os.path.join(PREPROCESSED_DIR, "item_user.npz")
USER_ITEMS_NPZ = os.path.join(PREPROCESSED_DIR, "user_items.npz")
TFIDF_MATRIX_NPZ = os.path.join(PREPROCESSED_DIR, "tfidf_matrix.npz")
MAPS_PKL = os.path.join(PREPROCESSED_DIR, "maps.pkl")

# PostgreSQL 데이터베이스 연결 설정
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "recommendation_db"
DB_USER = "postgres"
DB_PASSWORD = "your_password"  # 실제 비밀번호로 변경하세요

# 연결 문자열 (asyncpg 형식)
DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"