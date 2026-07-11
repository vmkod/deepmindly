import re


def clean_title(raw_title: str):
    if not raw_title or not raw_title.strip():
        return ""

    cleaned = (raw_title.replace("\u200e", "")
               .replace("\u200b", "")
               .replace("\xa0", " ")
               .strip()
    )

    #for telegram
    cleaned = re.sub(r"^\(\d+\)\s*", "", cleaned)
    cleaned = re.sub(r"\s*[-—–]\s*\(\d+\)$", "", cleaned)

    #for browsers
    cleaned = re.sub(r"\s*[-—–]\s*Личный:\s*Microsoft\s*Edge$", "", cleaned, flags=re.IGNORECASE)
    browsers = r"Google\s+Chrome|Mozilla\s+Firefox|Яндекс\s+Браузер|Opera|Brave"
    cleaned = re.sub(rf"\s*[-—–]\s*({browsers})$", "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip()

    ignore_keywords = [
        "новая вкладка", "экспресс-панель", "новая приватная вкладка",
        "private new tab", "новое окно",
        "проводник", "диспетчер задач", "параметры", "поиск",
        "загрузки", "рабочий стол", "корзина"
    ]

    if cleaned.lower() in ignore_keywords or len(cleaned) < 3:
        return ""

    return cleaned.strip()