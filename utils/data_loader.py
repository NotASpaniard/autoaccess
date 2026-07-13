import json
from pathlib import Path

# File dữ liệu mặc định: <project>/data/accounts.json
DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "accounts.json"

REQUIRED_FIELDS = {"username", "email", "password"}


def load_accounts(file_path: str = None) -> list[dict]:
    """Đọc danh sách tài khoản từ file JSON và trả về list các dict.

    Mỗi tài khoản bắt buộc có: username, email, password.
    Trường full_name là tùy chọn.
    """
    path = Path(file_path) if file_path else DEFAULT_DATA_FILE

    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {path}")

    with open(path, "r", encoding="utf-8") as f:
        accounts = json.load(f)

    if not isinstance(accounts, list):
        raise ValueError("File dữ liệu phải là một mảng (list) các tài khoản.")

    # Kiểm tra các trường bắt buộc
    for i, acc in enumerate(accounts):
        if not isinstance(acc, dict):
            raise ValueError(f"Tài khoản #{i} không phải dạng object.")
        missing = REQUIRED_FIELDS - acc.keys()
        if missing:
            raise ValueError(f"Tài khoản #{i} thiếu trường bắt buộc: {sorted(missing)}")

    return accounts
