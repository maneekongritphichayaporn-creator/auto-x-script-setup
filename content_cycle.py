from datetime import date, datetime, timedelta, timezone


CONTENT_TOPICS_BY_WEEKDAY = {
    0: "technology",
    1: "ai",
    2: "cyber_threats",
    3: "scams",
    4: "scam_prevention",
    5: "hacking_101",
    6: "thai_law",
}
THAILAND_TIMEZONE = timezone(timedelta(hours=7), name="Asia/Bangkok")


def topic_for_date(current_date: date) -> str:
    return CONTENT_TOPICS_BY_WEEKDAY[current_date.weekday()]


def thailand_today() -> date:
    return datetime.now(THAILAND_TIMEZONE).date()
