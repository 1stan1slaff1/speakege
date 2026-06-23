import uuid

from fastapi import Request, Response

GUEST_ID_COOKIE_NAME = "guest_id"
GUEST_ID_MAX_AGE_SECONDS = 60 * 60 * 24 * 365


def get_or_create_guest_id(request: Request, response: Response) -> str:
    guest_id = request.cookies.get(GUEST_ID_COOKIE_NAME)
    if guest_id:
        return guest_id

    guest_id = str(uuid.uuid4())
    response.set_cookie(
        key=GUEST_ID_COOKIE_NAME,
        value=guest_id,
        max_age=GUEST_ID_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production when HTTPS is enforced.
        path="/",
    )
    return guest_id
