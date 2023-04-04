from fastapi import Body, Depends, HTTPException
from fastapi.routing import APIRouter
from pydantic import parse_obj_as
from tortoise import transactions

from app.models.group import Group, GroupInPost
from app.models.user import User, UserInFront, UserInToken
from app.utils.tokens import get_user_in_token

router = APIRouter()


@router.get("/", description="On ne retourne que les groupes de l'utilisateur")
async def get_groups(user: UserInToken = Depends(get_user_in_token)):
    if user.admin is True:
        return await Group.all()
    else:
        return await Group.filter(owner_id=user.id)


@router.get("/{group_id}")
async def get_group(group_id: int, user: UserInToken = Depends(get_user_in_token)):
    group = await Group.get_or_none(id=group_id).prefetch_related("friends", "owner","friends")
    if group is None:
        raise HTTPException(status_code=404, detail="Group does not exists")
    if group.owner_id != user.id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    # show friends in group
    friends = parse_obj_as(list[UserInFront], friends)
    return {
        "id": group.id,
        "name": group.name,
        "owner": parse_obj_as(UserInFront, group.owner),
        "friends": friends
    }


@router.put("/{group_id}")
async def update_group(group_id: int, data: GroupInPost, user: UserInToken = Depends(get_user_in_token)):
    group = await Group.get_or_none(id=group_id).prefetch_related("owner")
    if group is None:
        raise HTTPException(status_code=404, detail="Group does not exists")
    if group.owner_id != user.id and user.admin is False:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this group")
    group.name = data.name
    await group.save()
    return {"message": "Group updated"}


@router.delete("/{group_id}")
async def delete_group(group_id: int, user: UserInToken = Depends(get_user_in_token)):
    group = await Group.get_or_none(id=group_id).prefetch_related("owner")
    if group is None:
        raise HTTPException(status_code=404, detail="Group does not exists")
    if group.owner_id != user.id and user.admin is False:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this group")
    await group.delete()
    return {"message": "Group deleted"}


@router.post("/")
async def create_group(group: GroupInPost, user: UserInToken = Depends(get_user_in_token)):
    userInDB = await User.get_or_none(id=user.id)
    group = Group(name=group.name, owner=userInDB)
    await group.save()
    return group


@router.post("/{group_id}/friends")
@transactions.atomic()
async def add_friends_to_group(group_id: int, friends: list[int], user: UserInToken = Depends(get_user_in_token)):
    if user.id in friends:
        raise HTTPException(
            status_code=403, detail="Forbidden you can't add yourself to the group")
    group = await Group.get_or_none(id=group_id).prefetch_related("friends", "owner")
    if group is None:
        raise HTTPException(status_code=404,
                            detail="Group does not exists")
    if group.owner_id != user.id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    # ajoutes les amis au groupe sans les charger de la base de données
    for friend in friends:
        await group.friends.add(await User.get(id=friend))
    return {"message": "ok"}


@router.delete("/{group_id}/friends/{user_id}")
async def delete_friends_from_group(group_id: int, user_id: int, user: UserInToken = Depends(get_user_in_token)):
    group = await Group.get_or_none(id=group_id).prefetch_related("friends", "owner")
    if group is None:
        raise HTTPException(status_code=404,
                            detail="Group does not exists")
    if group.owner_id != user.id and user.admin is False:
        raise HTTPException(status_code=403, detail="Forbidden")
    userInDB = await User.get_or_none(id=user_id)
    await group.friends.remove(userInDB)
    return {"message": "user removed from group", "user": parse_obj_as(UserInFront, userInDB)}
