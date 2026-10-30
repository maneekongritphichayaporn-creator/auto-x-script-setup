import time
from datetime import datetime

from dotenv import load_dotenv
from google.genai.errors import APIError

from content_cycle import thailand_today, topic_for_date
from main import generate_post, required_env


TEST_INTERVAL_SECONDS = 5 * 60


def main() -> None:
    load_dotenv()
    gemini_api_key = required_env("GEMINI_API_KEY")

    print("Local Gemini test started. No posts will be sent to X.")
    try:
        while True:
            started_at = time.monotonic()
            today = thailand_today()
            topic = topic_for_date(today)
            print(
                f"\n[{datetime.now().astimezone().isoformat(timespec='seconds')}] "
                f"Generating today's topic: {topic}"
            )

            try:
                tweet_text = generate_post(gemini_api_key, topic, today)
            except APIError as error:
                print(
                    "Gemini API request failed "
                    f"(HTTP {error.code}): {error.message}"
                )
            else:
                print("Generated text:")
                print("-" * 40)
                print(tweet_text)
                print("-" * 40)

            remaining = TEST_INTERVAL_SECONDS - (time.monotonic() - started_at)
            if remaining > 0:
                print("Next attempt in 5 minutes. Press Ctrl+C to stop.")
                time.sleep(remaining)
    except KeyboardInterrupt:
        print("\nLocal Gemini test stopped.")


if __name__ == "__main__":
    main()
