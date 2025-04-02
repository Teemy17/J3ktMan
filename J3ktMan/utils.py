from datetime import datetime


def epoch_to_date(epoch: int) -> str:
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d")


def date_to_epoch(date_str: str) -> int:
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
