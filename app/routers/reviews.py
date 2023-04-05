from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User, UserInToken
from app.models.review import Review, ReviewInPost, ReviewInUpdate
from datetime import date, timedelta, datetime, timezone
from tortoise.functions import Avg
from app.models.trip import Trip
from app.utils.tokens import get_user_in_token


router = APIRouter()


@router.post("/")
async def create_review(review: ReviewInPost, user: UserInToken = Depends(get_user_in_token)):
    userInDB = await User.get_or_none(id=user.id)
    userReviewed = await User.get_or_none(id=review.user_rated)
    # On vérifie que les deux utilisateurs concernés existent dans la bdd.
    if userInDB is None:
        raise HTTPException(status_code=404, detail="User does not exists !")
    if userReviewed is None:
        raise HTTPException(
            status_code=404, detail="Rated user does not exists !")

    # On vérifie que le Trip que l'on essaie de noter existe bien et qu'il n'est pas déjà noté
    # par l'utilisateur courant pour la personne notée
    trip_reviewed = await Trip.get_or_none(id=review.trip_rated).prefetch_related('passengers', 'driver')
    if trip_reviewed is None:
        raise HTTPException(status_code=404, detail="Trip not found !")

    ratings = await Review.get_or_none(rated=review.user_rated, author=user.id, trip=review.trip_rated)
    if ratings is not None:
        raise HTTPException(
            status_code=403, detail="A review has already been set for this trip and the rated user !")

    # On vérifie que la personne qui note et la personne notée ont bien fait partie du trajet.
    # On vérifie également que la date du trajet est passée.

    # -> Passagers du trajet
    if not (userInDB in trip_reviewed.passengers and userReviewed == trip_reviewed.driver) and not (userReviewed in trip_reviewed.passengers and userInDB == trip_reviewed.driver):
        raise HTTPException(
            status_code=403, detail="One of the concerned user was not in the trip rated !")
    # -> Vérification que la personne ne se note pas elle-même
    if userInDB == userReviewed:
        raise HTTPException(
            status_code=403, detail="You cannot rate yourself !")

    # -> Date du trajet
    if trip_reviewed.date >= datetime.now().astimezone():
        raise HTTPException(
            status_code=403, detail="You cannot rate this trip : it didn't happen yet !")

        # On sauvegarde l'avis dans la BDD.
    reviewInDB = await Review(author=userInDB, rated=userReviewed,
                              trip=trip_reviewed, rating=review.rating)
    await reviewInDB.save()

    return {"message": "ok"}


@router.get("/")
async def get_user_review(user: UserInToken = Depends(get_user_in_token)):
    # recupere les review créées par l'utilisateur
    reviews = await Review.filter(author_id=user.id).values("id", "date", "rating", "trip_id", "rated_id")

    return {
        "reviews": reviews
    }


@router.get("/me")
async def get_user_rating(user: UserInToken = Depends(get_user_in_token)):
    # recupere la moyenne des notes recu
    avg = await Review.filter(rated=user.id).annotate(avg=Avg("rating")).values("avg")
    if (avg[0] == "null"):
        raise HTTPException(
            status_code=404, detail="No reviews were left for this user !")
    return avg[0]


@router.get("/{user_id}}")
async def get_user_rating_withID(user_id: int, user: UserInToken = Depends(get_user_in_token)):
    userInDB = User.get_or_none(id=user_id)
    if (userInDB is None):
        raise HTTPException(
            status_code=404, detail="User does not exists")

    # recupere la moyenne des notes recu pour l'id de l'utilisateur concerné
    avg = await Review.filter(rated=user_id).annotate(avg=Avg("rating")).values("avg")

    if (avg[0] == "null"):
        raise HTTPException(
            status_code=404, detail="No reviews were left for this user !")
    return avg[0]


@router.put("/{review_id}")
async def update_review(review_id: int, patchedReview: ReviewInUpdate, user: UserInToken = Depends(get_user_in_token)):
    review = await Review.get_or_none(id=review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review does not exist")
    if review.author_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this review")
    if patchedReview.rating > 5 or patchedReview.rating < 0:
        raise HTTPException(
            status_code=403, detail="Rating must be between 0 and 5")
    review.rating = patchedReview.rating
    await review.save()
    return {"message": "Review updated"}


@router.delete("/{review_id}")
async def delete_review(review_id: int, user: UserInToken = Depends(get_user_in_token)):
    review = await Review.get_or_none(id=review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review does not exist")
    if review.author_id != user.id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    await review.delete()
    return {"message": "ok"}
