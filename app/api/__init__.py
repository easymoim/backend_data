from fastapi import APIRouter
from app.api import (
    auth,
    user,
    meeting,
    participant,
    time_candidate,
    time_vote,
    place,
    place_candidate,
    place_vote,
    review,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(meeting.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(participant.router, prefix="/participants", tags=["participants"])
api_router.include_router(time_candidate.router, prefix="/time-candidates", tags=["time-candidates"])
api_router.include_router(time_vote.router, prefix="/time-votes", tags=["time-votes"])
api_router.include_router(place.router, prefix="/places", tags=["places"])
api_router.include_router(place_candidate.router, prefix="/place-candidates", tags=["place-candidates"])
api_router.include_router(place_vote.router, prefix="/place-votes", tags=["place-votes"])
api_router.include_router(review.router, prefix="/reviews", tags=["reviews"])

