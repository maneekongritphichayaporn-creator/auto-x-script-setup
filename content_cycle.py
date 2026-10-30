from datetime import date, datetime, timedelta, timezone


CONTENT_TOPICS_BY_WEEKDAY = {
    0: "technology_ai",
    1: "thai_law",
    2: "conversation_question",
    3: "general_knowledge",
    4: "tools_apps",
    5: "coping_methods",
    6: "weekly_news",
}
THAILAND_TIMEZONE = timezone(timedelta(hours=7), name="Asia/Bangkok")


def topic_for_date(current_date: date) -> str:
    return CONTENT_TOPICS_BY_WEEKDAY[current_date.weekday()]


def thailand_today() -> date:
    return datetime.now(THAILAND_TIMEZONE).date()
