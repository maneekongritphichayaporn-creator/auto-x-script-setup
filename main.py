import argparse
import json
import os
from datetime import date
from typing import TypedDict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import tweepy
from dotenv import load_dotenv

from content_cycle import thailand_today, topic_for_date


class XCredentials(TypedDict):
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str


MAX_GENERATED_POST_LENGTH = 140
MAX_GENERATION_TOKENS = 1200
MAX_GENERATION_ATTEMPTS = 2
OPENROUTER_MODEL = "openrouter/free"
OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"
TOPIC_PROMPTS = {
    "technology": (
        "เล่าเรื่องเทคโนโลยีน่ารู้ อธิบายหลักการหรือประโยชน์ให้เข้าใจง่าย "
        "เลือกข้อเท็จจริงที่ไม่ต้องอาศัยข้อมูลข่าวล่าสุด"
    ),
    "ai": (
        "เล่าเรื่อง AI น่ารู้ เช่น แนวคิด การใช้งานอย่างรับผิดชอบ หรือข้อจำกัด "
        "อธิบายให้เข้าใจง่ายและไม่กล่าวอ้างเกินจริง"
    ),
    "cyber_threats": (
        "อธิบายภัยทางไซเบอร์ที่คนทั่วไปควรรู้ เช่น phishing, มัลแวร์ หรือการขโมยบัญชี "
        "เน้นสัญญาณเตือนและผลกระทบ ไม่ให้ขั้นตอนโจมตีหรือวิธีทำอันตราย"
    ),
    "scams": (
        "ยกตัวอย่างรูปแบบกลโกงที่พบได้ทั่วไป เช่น แอบอ้างเป็นเจ้าหน้าที่หรือหลอกลงทุน "
        "ช่วยให้ผู้อ่านสังเกตสัญญาณเตือน โดยไม่สร้างข้อความหลอกลวงที่นำไปใช้จริงได้"
    ),
    "scam_prevention": (
        "แนะนำวิธีป้องกัน scammer ที่ทำได้จริง เช่น หยุดตรวจสอบก่อนโอน "
        "ไม่กดลิงก์ที่น่าสงสัย และติดต่อหน่วยงานผ่านช่องทางทางการ"
    ),
    "hacking_101": (
        "สอนแนวคิดพื้นฐานด้าน cybersecurity หรือ hacking ในเชิงป้องกัน "
        "เช่น หลักการยืนยันตัวตน สิทธิ์การเข้าถึง หรือการทำงานของเครือข่าย "
        "เน้นการเรียนรู้ในระบบของตนเองหรือแล็บที่ได้รับอนุญาตเท่านั้น "
        "ห้ามสอนเจาะระบบจริง ขโมยข้อมูล หลบเลี่ยงการตรวจจับ หรือให้ขั้นตอนโจมตี"
    ),
    "thai_law": (
        "ให้ความรู้ทั่วไปเกี่ยวกับกฎหมายไทยด้านดิจิทัล เช่น พ.ร.บ.คอมพิวเตอร์ หรือ PDPA "
        "ไม่มีการค้นเว็บ จึงห้ามระบุมาตรา โทษ หรือรายละเอียดที่ไม่มั่นใจ "
        "ไม่ใช่คำปรึกษากฎหมาย และควรแนะนำให้ตรวจสอบข้อมูลล่าสุดจากแหล่งทางการ"
    ),
}


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def generate_post(openrouter_api_key: str, topic: str, current_date: date) -> str:
    if topic not in TOPIC_PROMPTS:
        raise ValueError(f"Unknown content topic: {topic}")

    prompt = (
        f"{TOPIC_PROMPTS[topic]} "
        f"วันที่ {current_date.isoformat()} "
        f"เขียนโพสต์ภาษาไทยสำหรับ X ไม่เกิน {MAX_GENERATED_POST_LENGTH} ตัวอักษร "
        "รวมแฮชแท็ก 1-2 แท็กถ้าเหมาะสม "
        "ตอบเฉพาะข้อความโพสต์ ไม่ใส่คำเกริ่นหรือ Markdown "
        "ไม่มีการค้นเว็บ หากไม่มั่นใจในข้อเท็จจริง ให้เลือกเรื่องอื่นที่มั่นใจ"
    )
    messages = [{"role": "user", "content": prompt}]

    for attempt in range(MAX_GENERATION_ATTEMPTS):
        request = Request(
            OPENROUTER_CHAT_COMPLETIONS_URL,
            data=json.dumps(
                {
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "max_tokens": MAX_GENERATION_TOKENS,
                }
            ).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=60) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {}
            api_error = (
                error_data.get("error", {}) if isinstance(error_data, dict) else {}
            )
            if isinstance(api_error, dict):
                message = api_error.get("message", "")
            elif isinstance(api_error, str):
                message = api_error
            else:
                message = ""
            if not message:
                message = error_body or exc.reason
            message = message.replace(openrouter_api_key, "[REDACTED]")
            raise RuntimeError(
                f"OpenRouter API request failed (HTTP {exc.code}): {message}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Could not connect to OpenRouter: {exc.reason}") from exc

        choices = (
            response_data.get("choices") if isinstance(response_data, dict) else None
        )
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("OpenRouter returned no choices.")
        choice = choices[0]
        message_data = choice.get("message") if isinstance(choice, dict) else None
        content = message_data.get("content") if isinstance(message_data, dict) else None
        if isinstance(content, str):
            tweet_text = content.strip()
        elif isinstance(content, list):
            text_parts = [
                part["text"]
                for part in content
                if isinstance(part, dict)
                and part.get("type") == "text"
                and isinstance(part.get("text"), str)
            ]
            tweet_text = "".join(text_parts).strip()
        else:
            finish_reason = (
                choice.get("finish_reason") if isinstance(choice, dict) else None
            )
            message_fields = (
                ", ".join(sorted(message_data))
                if isinstance(message_data, dict)
                else "unavailable"
            )
            response_model = (
                response_data.get("model", "unknown")
                if isinstance(response_data, dict)
                else "unknown"
            )
            raise RuntimeError(
                "OpenRouter returned no text "
                f"(model={response_model}, finish_reason={finish_reason}, "
                f"message_fields={message_fields}). Try the request again or select "
                "a different text-generation model. If finish_reason is 'length', "
                "the model may have used its token budget for reasoning."
            )
        if not tweet_text:
            raise ValueError("OpenRouter returned an empty post.")
        if len(tweet_text) <= MAX_GENERATED_POST_LENGTH:
            return tweet_text
        if attempt + 1 == MAX_GENERATION_ATTEMPTS:
            raise ValueError(
                f"Generated post is {len(tweet_text)} characters after "
                f"{MAX_GENERATION_ATTEMPTS} attempts; "
                f"keep it at most {MAX_GENERATED_POST_LENGTH}."
            )

        messages.extend(
            [
                {"role": "assistant", "content": tweet_text},
                {
                    "role": "user",
                    "content": (
                        "ย่อโพสต์ข้างต้นให้เหลือไม่เกิน "
                        f"{MAX_GENERATED_POST_LENGTH} ตัวอักษร โดยคงใจความสำคัญ "
                        "ตอบเฉพาะข้อความโพสต์"
                    ),
                },
            ]
        )

    raise RuntimeError("Post generation ended without a result.")


def post_to_x(tweet_text: str, x_credentials: XCredentials) -> str:
    x_client = tweepy.Client(**x_credentials)
    result = x_client.create_tweet(text=tweet_text)
    if not result.data or not result.data.get("id"):
        raise RuntimeError("X did not return a post ID; the post may not have been created.")
    return result.data["id"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and publish a daily X post.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and print the post without publishing it to X.",
    )
    args = parser.parse_args()

    load_dotenv()

    openrouter_api_key = required_env("OPENROUTER_API_KEY")
    today = thailand_today()
    topic = topic_for_date(today)
    print(f"Today's content topic: {topic}")

    tweet_text = generate_post(openrouter_api_key, topic, today)
    if args.dry_run:
        print(f"Generated post ({len(tweet_text)} characters):")
        print(tweet_text)
        return

    x_credentials: XCredentials = {
        "consumer_key": required_env("X_API_KEY"),
        "consumer_secret": required_env("X_API_SECRET"),
        "access_token": required_env("X_ACCESS_TOKEN"),
        "access_token_secret": required_env("X_ACCESS_TOKEN_SECRET"),
    }
    tweet_id = post_to_x(tweet_text, x_credentials)
    print(f"Successfully posted to X (ID: {tweet_id}).")


if __name__ == "__main__":
    main()
