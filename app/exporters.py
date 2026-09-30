from pathlib import Path
from uuid import uuid4

from fpdf import FPDF
from PIL import Image

from app.config import BASE_DIR, EXPORT_DIR


def safe_text(text):

    if text is None:
        return ""

    return (
        str(text)
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def save_pdf(layout: list):

    filename = f"comic_{uuid4().hex[:10]}.pdf"

    output_path = EXPORT_DIR / filename

    pdf = FPDF(
        "P",
        "mm",
        "A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        # Panel title
        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        title = (
            f"Panel {panel['panel_number']}: "
            f"{panel['title']}"
        )

        pdf.multi_cell(
            0,
            10,
            safe_text(title)
        )

        # Image
        image_url = panel.get(
            "image_path",
            ""
        )

        relative_path = image_url.replace(
            "/static/",
            ""
        )

        image_path = (
            BASE_DIR
            / "static"
            / relative_path
        )

        if image_path.exists():

            with Image.open(
                image_path
            ) as image:

                width, height = image.size

            max_width = 180
            max_height = 105

            scale = min(
                max_width / width,
                max_height / height
            )

            display_width = width * scale
            display_height = height * scale

            pdf.image(
                str(image_path),
                x=15,
                y=32,
                w=display_width,
                h=display_height
            )

        pdf.ln(110)

        # Scene description
        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            safe_text(
                panel.get(
                    "scene_description",
                    ""
                )
            )
        )

        # Caption
        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        pdf.multi_cell(
            0,
            6,
            safe_text(
                panel.get(
                    "caption",
                    ""
                )
            )
        )

        # Narration
        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            6,
            safe_text(
                panel.get(
                    "narration",
                    ""
                )
            )
        )

        # Dialogue
        for dialogue in panel.get(
            "dialogue",
            []
        ):

            pdf.ln(1)

            pdf.set_font(
                "Helvetica",
                "I",
                10
            )

            pdf.multi_cell(
                0,
                6,
                safe_text(dialogue)
            )

    pdf.output(
        str(output_path)
    )

    return f"/static/exports/{filename}"