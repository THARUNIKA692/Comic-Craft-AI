from fastapi import FastAPI

from fastapi.staticfiles import (
    StaticFiles
)

from app.config import (
    STATIC_DIR,
    TEMPLATES_DIR,
)

from app.routes import router


app = FastAPI(

    title="ComicCraft",

    description=(
        "AI Comic Story Creator "
        "using Gemini and Hugging Face"
    ),

    version="1.0.0"
)


# --------------------------------
# STATIC FILES
# --------------------------------

app.mount(

    "/static",

    StaticFiles(
        directory=str(
            STATIC_DIR
        )
    ),

    name="static"
)


# --------------------------------
# ROUTES
# --------------------------------

app.include_router(
    router
)


# --------------------------------
# HEALTH CHECK
# --------------------------------

@app.get("/health")
async def health():

    return {

        "status": "ok",

        "application": "ComicCraft"
    }