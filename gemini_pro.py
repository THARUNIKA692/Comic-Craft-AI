import json
import time

from google import genai
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    GEMINI_STORY_MODEL,
)

from app.schemas import PanelStory


def get_gemini_client():

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to .env."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def generate_story(
    outline: list,
    character_name: str,
    tone: str
):

    client = get_gemini_client()

    outline_json = json.dumps(
        outline,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are an expert comic book writer.

Expand the following comic outline into a complete five-panel comic.

MAIN CHARACTER:
{character_name}

TONE:
{tone}

OUTLINE:

{outline_json}

For every panel generate:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

Rules:

1. Keep the same story.
2. Keep the same character.
3. Preserve panel order.
4. Narration should be concise.
5. Dialogue should sound natural.
6. Each panel should move the story forward.
7. Do not change the image prompt unnecessarily.
8. Return ONLY valid JSON.

Required JSON:

{{
    "panels": [
        {{
            "panel_number": 1,
            "title": "Title",
            "scene_description": "Description",
            "caption": "Caption",
            "narration": "Narration",
            "dialogue": [
                "Character: Dialogue"
            ],
            "image_prompt": "Image prompt"
        }}
    ]
}}
"""

    max_retries = 4
    base_delay = 5

    for attempt in range(max_retries):

        try:

            print(
                f"Gemini story attempt "
                f"{attempt + 1}/{max_retries}..."
            )

            response = client.models.generate_content(

                model=GEMINI_STORY_MODEL,

                contents=prompt,

                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty story."
                )

            try:

                data = json.loads(response.text)

            except json.JSONDecodeError as error:

                raise RuntimeError(
                    f"Invalid Gemini JSON: {error}"
                )

            if "panels" not in data:

                raise RuntimeError(
                    "Story response does not contain panels."
                )

            panels = []

            for panel in data["panels"]:

                panels.append(
                    PanelStory.model_validate(panel)
                )

            print("Gemini story generated successfully.")

            return [
                panel.model_dump()
                for panel in panels
            ]

        except Exception as error:

            error_text = str(error)

            if "503" in error_text or "UNAVAILABLE" in error_text:

                if attempt < max_retries - 1:

                    delay = base_delay * (2 ** attempt)

                    print(
                        f"Gemini is temporarily busy. "
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

                else:

                    raise RuntimeError(
                        "Gemini is currently experiencing high demand. "
                        "Please try again after a few minutes."
                    )

            else:

                raise