import joblib
from src.config import DOCS_PATH, VEC_PATH, GV_PATH

def load_analyzed_texts():
    """
    분석된 텍스트 데이터를 로드합니다.
    Returns:
        dict: group_id와 텍스트 매핑
    """
    try:
        with open(DOCS_PATH, "rb") as f:
            analyzed_texts = joblib.load(f)
        return analyzed_texts
    except Exception as e:
        raise RuntimeError(f"Failed to load analyzed texts from {DOCS_PATH}: {str(e)}")

def load_tfidf():
    """
    TF-IDF 벡터라이저와 그룹 벡터를 로드합니다.
    Returns:
        tuple: (tfidf_vectorizer, group_vectors)
    """
    try:
        with open(VEC_PATH, "rb") as f:
            tfidf = joblib.load(f)
        with open(GV_PATH, "rb") as f:
            group_vectors = joblib.load(f)
        return tfidf, group_vectors
    except Exception as e:
        raise RuntimeError(f"Failed to load TF-IDF data from {VEC_PATH} or {GV_PATH}: {str(e)}")