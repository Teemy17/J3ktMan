from datetime import datetime


def epoch_to_date(epoch) -> str:
    """
    Convert a Unix epoch timestamp to a date string in the format YYYY-MM-DD.
    """
    if epoch is None:
        return ""
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d")


def date_to_epoch(date_str: str) -> int:
    """
    Convert a date string in the format YYYY-MM-DD to a Unix epoch timestamp.
    """
    if date_str is None or date_str == "":
        return 0
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
