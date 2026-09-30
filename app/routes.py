from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.schemas import PromptRequest
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf


router = APIRouter()

templates = Jinja2Templates(directory="templates")


def create_comic(request_data: PromptRequest):

    outline = generate_outline(
        request_data.story_prompt,
        request_data.character_name,
        request_data.setting,
        request_data.tone,
        request_data.art_style
    )

    story = generate_story(
        outline,
        request_data.character_name,
        request_data.tone
    )

    image_paths = []

    for panel in story:

        image_path = generate_image(
            panel["image_prompt"],
            panel["panel_number"]
        )

        image_paths.append(image_path)

    layout = build_comic_layout(
        story,
        image_paths
    )

    pdf_path = save_pdf(layout)

    return layout, pdf_path


@router.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):

    try:

        request_data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )

        layout, pdf_path = create_comic(
            request_data
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": pdf_path
            }
        )

    except Exception as error:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(error)
            },
            status_code=500
        )


@router.post("/generate-comic/json")
async def generate_comic_json(
    payload: PromptRequest
):

    try:

        layout, pdf_path = create_comic(
            payload
        )

        return JSONResponse(
            {
                "success": True,
                "layout": layout,
                "pdf_path": pdf_path
            }
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.post("/test-image")
async def test_image(
    prompt: str = Form(...)
):

    try:

        image_path = generate_image(
            prompt,
            0
        )

        return {
            "success": True,
            "image_path": image_path
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.get("/export-success")
async def export_success(
    request: Request,
    pdf_path: str = ""
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_path": pdf_path
        }
    )