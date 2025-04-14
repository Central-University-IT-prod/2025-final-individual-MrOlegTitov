from .routers import clients, advertisers, campaigns, ads, statistics, time, s3, gpt
from .utils import lifespan

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

app = FastAPI(lifespan=lifespan, title='AdsPlatform API')
app.include_router(s3.router)
app.include_router(clients.router)
app.include_router(advertisers.router)
app.include_router(campaigns.router)
app.include_router(ads.router)
app.include_router(statistics.router)
app.include_router(time.router)
app.include_router(gpt.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        content={'status': 'error', 'message': str(exc.detail)},
        status_code=exc.status_code,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        content={
            'status': 'error',
            'message': '; '.join(
                [
                    f"{'-> '.join(map(str, error.get('loc', tuple())))}: {error.get('msg', '')}"
                    for error in exc.errors()
                ]
            ),
        },
        status_code=400,
    )


@app.get('/')
async def root() -> str:
    return 'AdsPlatform API. PROOOOD!'
