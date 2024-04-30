from fastapi import BackgroundTasks, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool

import os
import time

from traceback import format_exc
from datetime import datetime

from .lib import database
from .lib import cache as cm

from .lib.api import popular_ciks_request, top_ciks_request
from .lib.backup import save_collections

from .filer import create_filer_try, create_filer_replace

environment = os.environ["ENVIRONMENT"]

cache = cm.cache
router = APIRouter(
    tags=["general"],
)

cwd = os.getcwd()
router.mount(f"{cwd}/static", StaticFiles(directory="static"), name="static")


@cache(24)
@router.get("/", status_code=200)
async def info():
    return {"message": "Hello World!"}


@cache
@router.get("/undefined", status_code=200)
async def info_undefined():
    return {"message": "Hello World!"}


def background_query(query_type, cik_list, background, query_function):
    query = cm.get_key(query_type)
    if query and query == "running":
        raise HTTPException(status_code=429, detail="Query already running.")

    cm.set_key_no_expiration(query_type, "running")

    for cik in cik_list:
        query_function(cik, background)

    cm.set_key_no_expiration(query_type, "stopped")


@router.get("/query", status_code=200, include_in_schema=False)
async def query_top(password: str, background: BackgroundTasks):
    if password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(detail="Unable to give access.", status_code=403)

    filer_ciks = top_ciks_request()
    filer_ciks.extend(popular_ciks_request())

    background.add_task(
        background_query, "query", filer_ciks, background, create_filer_try
    )

    return {"description": "Started querying filers."}


@router.get("/restore", status_code=200)
async def progressive_restore(password: str, background: BackgroundTasks):
    if password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(detail="Unable to give access.", status_code=403)

    filers = database.find_filers({}, {"cik": 1})
    all_ciks = [filer["cik"] for filer in filers]

    background.add_task(
        background_query, "restore", all_ciks, background, create_filer_replace
    )

    return {"description": "Started progressive restore of filers."}


def create_error(cik, e):
    stamp = str(datetime.now())
    cwd = os.getcwd()
    with open(f"{cwd}/static/errors/error-general-{stamp}.log", "w") as f:
        error_string = f"Failed to Query Filer {cik}\n{repr(e)}\n{format_exc()}"
        f.write(error_string)


@router.get("/backup", status_code=201)
async def backup(password: str, background: BackgroundTasks):
    if password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(detail="Unable to give access.", status_code=403)

    background.add_task(save_collections)
    return {"description": "Started backing up collections."}


@cache
@router.get("/favicon.ico", status_code=200)
async def favicon():
    return FileResponse(f"{cwd}/static/favicon.ico")
