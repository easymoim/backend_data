from fastapi import APIRouter
from app.api import (
    auth,
    users,
    meetings,
    participants,
    time_candidates,
    time_votes,
    places,
    place_candidates,
    place_votes,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(participants.router, prefix="/participants", tags=["participants"])
api_router.include_router(time_candidates.router, prefix="/time-candidates", tags=["time-candidates"])
api_router.include_router(time_votes.router, prefix="/time-votes", tags=["time-votes"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(place_candidates.router, prefix="/place-candidates", tags=["place-candidates"])
api_router.include_router(place_votes.router, prefix="/place-votes", tags=["place-votes"])

