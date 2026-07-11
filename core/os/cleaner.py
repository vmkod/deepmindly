def clean_title(raw_title: str):
    if not raw_title or not raw_title.strip():
        return ""
    return raw_title.strip()