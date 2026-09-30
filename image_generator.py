from io import BytesIO
from pathlib import Path
from uuid import uuid4

from huggingface_hub import InferenceClient

from PIL import Image

from app.config import (
    HF_API_KEY,
    HF_IMAGE_MODEL,
    PANEL_DIR,
)


def generate_image(
    image_prompt: str,
    panel_number: int
):

    if not HF_API_KEY:

        raise RuntimeError(
            "HF_API_KEY is missing. "
            "Please add your Hugging Face token to .env."
        )

    client = InferenceClient(
        provider="hf-inference",
        api_key=HF_API_KEY
    )

    final_prompt = f"""
{image_prompt}

Create a high-quality comic book illustration.

Requirements:

- cinematic composition
- clear main character
- consistent character appearance
- detailed environment
- expressive action
- dramatic lighting
- clean comic illustration
- no text
- no captions
- no watermark
"""

    result = client.text_to_image(

        prompt=final_prompt,

        model=HF_IMAGE_MODEL
    )

    if isinstance(result, Image.Image):

        image = result

    else:

        image = Image.open(
            BytesIO(result)
        )

    filename = (
        f"panel_{panel_number}_"
        f"{uuid4().hex[:8]}.png"
    )

    file_path = PANEL_DIR / filename

    image.convert("RGB").save(
        file_path,
        "PNG"
    )

    return (
        f"/static/panels/{filename}"
    )