import pandas as pd
from src.config import DATA_PATH

def load_data(user_index=None, core_only=True):
    """
    Parquet에서 데이터 로드
    Args:
        user_index (int, optional): 특정 사용자 데이터만 로드
        core_only (bool): 최소 열 로드 여부
    Returns:
        pd.DataFrame: 로드된 데이터
    """
    columns = ['user_index', 'asset_id', 'super_asset_nm', 'group_id'] if core_only else None
    filters = [('user_index', '==', user_index)] if user_index else None
    df = pd.read_parquet(DATA_PATH, columns=columns, filters=filters)
    print(f"✅ Loaded data from Parquet for user_index={user_index}")
    return df