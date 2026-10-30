import os
from datetime import date
from typing import TypedDict

import tweepy
from dotenv import load_dotenv
from google import genai
from google.genai import types

from content_cycle import thailand_today, topic_for_date


class XCredentials(TypedDict):
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str


MAX_POST_LENGTH = 280
GEMINI_MODEL = "gemini-3.8-flash"
TOPIC_PROMPTS = {
    "technology_ai": (
        "แนะนำ AI หรือตัวช่วยทำงานที่มีประโยชน์ หรือเทคโนโลยีใหม่ๆ พร้อมบอกจุดเด่นสั้นๆ "
        "หรือแชร์คีย์เวิร์ด/Prompt เด็ดประจำสัปดาห์ที่นำไปใช้ได้จริง"
    ),
    "thai_law": (
        "เล่าสิทธิที่ควรรู้หรือข้อกฎหมายไทยใกล้ตัว เช่น สัญญาง่ายๆ "
        "กฎหมายไซเบอร์ หรือลิขสิทธิ์ อธิบายเป็นข้อมูลทั่วไป ไม่ใช่คำปรึกษากฎหมาย "
        "และอย่าฟันธงหากตรวจสอบแหล่งข้อมูลทางการไม่ได้"
    ),
    "conversation_question": (
        "ตั้งคำถามชวนคิดที่ตอบง่ายและชวนให้คนมาแสดงความคิดเห็น เกี่ยวกับเทคโนโยลีหรือ Cybersecurity "
        "เช่น 'คุณเคยเจอข้อความหลอกลวงทางออนไลน์ไหม? แชร์ประสบการณ์ของคุณ!' "
        "ไม่ต้องเฉลยคำถาม"
    ),
    "general_knowledge": (
        "เล่าเกร็ดความรู้หรือ Fact จริงที่น่าประหลาดใจเกี่ยวกับ Cybersecurity, AI, Technology, หรือวิทยาศาสตร์ "
        "หรือประวัติศาสตร์ ใช้ภาษาย่อยง่ายและเลือกเรื่องที่ตรวจสอบได้"
    ),
    "tools_apps": (
        "แนะนำแอป Extension เบราว์เซอร์ หรือเว็บไซต์ฟรีที่มีประโยชน์ "
        "บอกว่าใช้ช่วยอะไรและเหมาะกับใคร ห้ามกล่าวอ้างว่าใช้ฟรีหากตรวจสอบไม่ได้"
    ),
    "coping_methods": (
        "แนะนำวิธีรับมือปัญหาภัยไซเบอร์ที่ทำได้จริงและปลอดภัย เช่น แก๊งคอลเซ็นเตอร์ "
        "ความเครียด หรือการบริหารเวลา"
    ),
    "weekly_news": (
        "ค้นหาและสรุป 3 ข่าวหรือเทรนด์ใหญ่ด้านเทคโนโลยี ไอที หรือ AI "
        "ที่เกิดขึ้นในสัปดาห์นี้ จบในโพสต์เดียว ระบุประเด็นให้แยกกันชัดเจน "
        "ห้ามแต่งข่าวหรือวันที่ขึ้นเอง"
    ),
}
GROUNDED_TOPICS = {"technology_ai", "thai_law", "tools_apps", "weekly_news"}


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def generate_post(gemini_api_key: str, topic: str, current_date: date) -> str:
    if topic not in TOPIC_PROMPTS:
        raise ValueError(f"Unknown content topic: {topic}")

    ai_client = genai.Client(
        api_key=gemini_api_key,
        http_options=types.HttpOptions(
            timeout=60_000,
            retry_options=types.HttpRetryOptions(attempts=2),
        ),
    )
    prompt = (
        f"{TOPIC_PROMPTS[topic]} "
        f"วันที่ {current_date.isoformat()} "
        "เขียนโพสต์ภาษาไทยสำหรับ X ไม่เกิน 260 ตัวอักษร "
        "รวมแฮชแท็ก 1-2 แท็กถ้าเหมาะสม "
        "ตอบเฉพาะข้อความโพสต์ ไม่ใส่คำเกริ่นหรือ Markdown "
        "ใช้ผลค้นหาเว็บสำหรับข้อมูลปัจจุบันและข้อกฎหมาย "
        "หากไม่มีข้อมูลที่เชื่อถือได้ ให้เลือกประเด็นอื่นที่ตรวจสอบได้"
    )
    config = None
    if topic in GROUNDED_TOPICS:
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

    response = ai_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )
    tweet_text = (response.text or "").strip()
    if not tweet_text:
        raise ValueError("Gemini returned an empty post.")
    if len(tweet_text) > MAX_POST_LENGTH:
        raise ValueError(
            f"Generated post is {len(tweet_text)} characters; "
            f"X allows at most {MAX_POST_LENGTH}."
        )
    return tweet_text


def post_to_x(tweet_text: str, x_credentials: XCredentials) -> str:
    x_client = tweepy.Client(**x_credentials)
    result = x_client.create_tweet(text=tweet_text)
    if not result.data or not result.data.get("id"):
        raise RuntimeError("X did not return a post ID; the post may not have been created.")
    return result.data["id"]


def main() -> None:
    load_dotenv()

    gemini_api_key = required_env("GEMINI_API_KEY")
    today = thailand_today()
    topic = topic_for_date(today)
    print(f"Today's content topic: {topic}")

    x_credentials: XCredentials = {
        "consumer_key": required_env("X_API_KEY"),
        "consumer_secret": required_env("X_API_SECRET"),
        "access_token": required_env("X_ACCESS_TOKEN"),
        "access_token_secret": required_env("X_ACCESS_TOKEN_SECRET"),
    }

    tweet_text = generate_post(gemini_api_key, topic, today)
    tweet_id = post_to_x(tweet_text, x_credentials)
    print(f"Successfully posted to X (ID: {tweet_id}).")


if __name__ == "__main__":
    main()
