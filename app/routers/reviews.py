from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User, UserInToken
from app.models.review import Review, ReviewInPost
from app.models.trip import Trip
from app.utils.tokens import get_user_in_token


router = APIRouter()

# En attente de test
@router.delete("/{review_id}")
async def delete_review(review_id: int, user: UserInToken = Depends(get_user_in_token)):
    review = await Review.get(id=review_id)
    if review is None :
        raise HTTPException(status_code=404, detail="Review does not exist")
    if review.author_id != user.id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    await review.delete()
    return {"message": "review deleted"}
