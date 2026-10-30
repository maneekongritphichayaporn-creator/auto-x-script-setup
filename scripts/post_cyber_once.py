from dotenv import load_dotenv

from content_cycle import thailand_today
from main import XCredentials, generate_post, post_to_x, required_env


def main() -> None:
    load_dotenv()

    gemini_api_key = required_env("GEMINI_API_KEY")
    x_credentials: XCredentials = {
        "consumer_key": required_env("X_API_KEY"),
        "consumer_secret": required_env("X_API_SECRET"),
        "access_token": required_env("X_ACCESS_TOKEN"),
        "access_token_secret": required_env("X_ACCESS_TOKEN_SECRET"),
    }

    today = thailand_today()
    print("Generating one general cybersecurity post with Gemini...")
    tweet_text = generate_post(gemini_api_key, "cybersecurity", today)
    print("Generated text:")
    print("-" * 40)
    print(tweet_text)
    print("-" * 40)

    print("Posting one post to X...")
    tweet_id = post_to_x(tweet_text, x_credentials)
    print(f"Posted successfully. Post ID: {tweet_id}")


if __name__ == "__main__":
    main()
