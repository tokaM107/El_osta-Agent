import os
import json
import time
from google.genai import Client, types
from dotenv import load_dotenv


load_dotenv()

client = Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)
SYSTEM_PROMPT = """
انت مساعد ذكي بتشرح رحلات مواصلات للناس بطريقة بسيطة ولطيفة.

المدخل JSON فيه:
- origin
- destination
- journeys: قائمة من البدائل، كل رحلة فيها id و text_summary

المطلوب:
- اكتب بالعامية المصرية
- اشرح كل رحلة في فقرة منفصلة بناءً على text_summary بتاعها
- لو مفيش رحلات قول: "مع الأسف مفيش رحلات مناسبة دلوقتي."
"""

def format_server_journeys_for_user_llm(
    journeys: list,
    origin: str,
    dest: str
) -> str:
    try:
        if not journeys:
            return "مع الأسف مفيش رحلات مناسبة دلوقتي."

        clean_journeys = [
            {"id": j.get("id"), "text_summary": j.get("text_summary", "")}
            for j in journeys
        ]

        payload = {
            "origin": origin,
            "destination": dest,
            "journeys": clean_journeys
        }

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[json.dumps(payload, ensure_ascii=False)],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0,
                        response_mime_type="text/plain",
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    )
                )
                return response.text
            except Exception as e:
                err = str(e)
                if "429" in err and attempt < 2:
                    wait = 3 * (attempt + 1)
                    print(f"[LLM FORMAT] Rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise

        return "حصلت مشكلة واحنا بنجهز الرحلات، جرب تاني."

    except Exception as e:
        print(f"[LLM FORMAT ERROR] {e}")
        return "حصلت مشكلة واحنا بنجهز الرحلات، جرب تاني."