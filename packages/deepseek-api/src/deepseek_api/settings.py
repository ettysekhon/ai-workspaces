import os

from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if __name__ == "__main__":
    print(f"Loaded settings: DEEPSEEK_API_KEY={DEEPSEEK_API_KEY}")
