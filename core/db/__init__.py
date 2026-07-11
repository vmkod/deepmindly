from .connect import get_connection, init_db
from .storage import WindowRecord, fetch_all_titles, save_window_title

__all__ = [
    "get_connection",
    "init_db",
    "WindowRecord",
    "save_window_title",
    "fetch_all_titles"
]