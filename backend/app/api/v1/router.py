from fastapi import APIRouter

from app.api.v1 import routes_auth, routes_cohort, routes_dialogues, routes_guest

router = APIRouter(prefix="/api/v1", tags=["v1"])
router.include_router(routes_auth.router)
router.include_router(routes_dialogues.router)
router.include_router(routes_guest.router)
router.include_router(routes_cohort.router)
