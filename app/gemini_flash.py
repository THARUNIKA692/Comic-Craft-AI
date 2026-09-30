import json
import time

from google import genai
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    GEMINI_OUTLINE_MODEL,
    PANEL_COUNT,
)

from app.schemas import PanelOutline


def get_gemini_client():

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
):

    client = get_gemini_client()

    prompt = f"""
You are an expert comic book story planner.

Create a coherent {PANEL_COUNT}-panel comic outline.

USER STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

IMPORTANT REQUIREMENTS:

1. Create exactly {PANEL_COUNT} panels.
2. The story must have a clear beginning, middle and ending.
3. Keep the same main character throughout.
4. Every panel must advance the story.
5. Make the scenes visually interesting.
6. Create a detailed image prompt for every panel.
7. The image prompt must describe:
   - character
   - environment
   - pose/action
   - camera/composition
   - lighting
   - art style
8. Do not include dialogue inside image_prompt.

Return ONLY valid JSON.

Required format:

{{
    "panels": [
        {{
            "panel_number": 1,
            "title": "Panel title",
            "scene_description": "Scene description",
            "image_prompt": "Detailed visual prompt"
        }}
    ]
}}
"""

    max_retries = 4
    base_delay = 5

    for attempt in range(max_retries):

        try:

            print(
                f"Gemini outline attempt "
                f"{attempt + 1}/{max_retries}..."
            )

            response = client.models.generate_content(

                model=GEMINI_OUTLINE_MODEL,

                contents=prompt,

                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            try:

                data = json.loads(response.text)

            except json.JSONDecodeError as error:

                raise RuntimeError(
                    f"Gemini returned invalid JSON: {error}"
                )

            if "panels" not in data:

                raise RuntimeError(
                    "Gemini response does not contain panels."
                )

            panels = []

            for panel in data["panels"]:

                panels.append(
                    PanelOutline.model_validate(panel)
                )

            if len(panels) != PANEL_COUNT:

                raise RuntimeError(
                    f"Expected {PANEL_COUNT} panels, "
                    f"but Gemini returned {len(panels)}."
                )

            print("Gemini outline generated successfully.")

            return [
                panel.model_dump()
                for panel in panels
            ]

        except Exception as error:

            error_text = str(error)

            # Retry only temporary server/capacity errors
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