import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.core.config import Settings, get_settings
from app.models.startup import (
    LatestStartupEnrichedResponse,
    LatestStartupLinksResponse,
    LatestStartupsReadableResponse,
)
from app.services.llm_extraction import StartupExtractionError, StartupValidationError
from app.services.yc_companies import YCCompanyService, YCScraperError

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/", include_in_schema=False)
async def homepage_redirect(
    settings: Settings = Depends(get_settings),
) -> RedirectResponse:
    return RedirectResponse(url=settings.frontend_url, status_code=307)


@router.get("/api/v1/startups/latest-links", response_model=LatestStartupLinksResponse)
async def latest_startup_links(
    settings: Settings = Depends(get_settings),
) -> LatestStartupLinksResponse:
    service = YCCompanyService(settings)

    try:
        return await service.fetch_latest_startup_links()
    except YCScraperError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from YC public sources.",
        ) from exc


@router.get("/api/v1/startups/latest", response_model=LatestStartupsReadableResponse)
async def latest_startup_profiles(
    settings: Settings = Depends(get_settings),
) -> LatestStartupsReadableResponse:
    service = YCCompanyService(settings)

    try:
        return await service.fetch_latest_startup_profiles_readable()
    except YCScraperError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from YC public sources.",
        ) from exc


@router.get("/api/v1/startups/latest-enriched", response_model=LatestStartupsReadableResponse)
async def latest_startup_profiles_enriched(
    settings: Settings = Depends(get_settings),
) -> LatestStartupsReadableResponse:
    service = YCCompanyService(settings)

    try:
        return await service.fetch_latest_startup_profiles_enriched_readable()
    except StartupValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except StartupExtractionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except YCScraperError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from upstream services.",
        ) from exc


@router.get("/api/v1/startups/current-batch-enriched", response_model=LatestStartupsReadableResponse)
async def current_batch_startup_profiles_enriched(
    limit: int = Query(default=200, ge=1, le=500),
    settings: Settings = Depends(get_settings),
) -> LatestStartupsReadableResponse:
    service = YCCompanyService(settings)

    try:
        return await service.fetch_latest_startup_profiles_enriched_readable(limit=limit)
    except StartupValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except StartupExtractionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except YCScraperError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from upstream services.",
        ) from exc
