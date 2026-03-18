from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user, require_admin
from ..models.user import User
from ..schemas.user import UserRead, UserUpdate, UserList
from ..utils.exceptions import not_found, forbidden
from ..utils.pagination import Pagination

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.email is not None:
        existing = db.query(User).filter(User.email == payload.email, User.id != current_user.id).first()
        if existing:
            from ..utils.exceptions import conflict
            raise conflict("Email already in use")
        current_user.email = payload.email
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("", response_model=UserList)
def list_users(
    pagination: Pagination = Depends(),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    total = db.query(User).count()
    users = db.query(User).offset(pagination.offset).limit(pagination.size).all()
    return {
        "items": users,
        **pagination.paginate(total),
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if user_id == admin.id:
        raise forbidden("Cannot delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise not_found("User")
    user.is_active = False
    db.commit()
    return None
