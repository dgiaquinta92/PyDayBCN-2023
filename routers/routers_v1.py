from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse, RedirectResponse
import models.models as md


router = APIRouter()


@router.get("/get-test", response_class=JSONResponse, tags=["TEST"])
async def get_test(name: md.Names):
    response = {}
    response["result"] = "Hello " + name
    return response
