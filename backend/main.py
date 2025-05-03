from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from sqlmodel import Field, SQLModel, create_engine, Relationship, Session, select
from sqlalchemy.orm import selectinload
from typing import Optional, List, Annotated, Literal
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4, UUID
from firebase_admin import auth as firebase_auth, credentials
import firebase_admin
import os
from dotenv import load_dotenv

# --------- USER ---------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    firebase_uid: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    name: str | None

    wishlists_created: List["Wishlist"] = Relationship(back_populates="creator", sa_relationship_kwargs={"foreign_keys": "[Wishlist.created_by_id]"})
    wishlist_links: List["WishlistUserLink"] = Relationship(back_populates="user")
    items_added: List["Item"] = Relationship(back_populates="added_by", sa_relationship_kwargs={"foreign_keys": "[Item.added_by_id]"})
    items_claimed: List["Item"] = Relationship(back_populates="claimed_by", sa_relationship_kwargs={"foreign_keys": "[Item.claimed_by_id]"})
    items_acquired: List["Item"] = Relationship(back_populates="acquired_by", sa_relationship_kwargs={"foreign_keys": "[Item.acquired_by_id]"})


# --------- WISHLIST ---------
class Wishlist(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    recipient_name: Optional[str]
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    invitation_id: UUID = Field(default_factory=uuid4, index=True, unique=True)

    creator: Optional[User] = Relationship(back_populates="wishlists_created", sa_relationship_kwargs={"foreign_keys": "[Wishlist.created_by_id]"})
    users: List["WishlistUserLink"] = Relationship(back_populates="wishlist")
    items: List["Item"] = Relationship(back_populates="wishlist")


# --------- ASSOCIATION TABLE: Wishlist ↔ User ---------
class WishlistUserLink(SQLModel, table=True):
    wishlist_id: int = Field(foreign_key="wishlist.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role: str

    wishlist: Optional[Wishlist] = Relationship(back_populates="users")
    user: Optional[User] = Relationship(back_populates="wishlist_links")


# --------- ITEM ---------
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wishlist_id: int = Field(foreign_key="wishlist.id")
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    added_by_id: int = Field(foreign_key="user.id")
    claimed_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    acquired_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    active: bool = Field(default=True)

    wishlist: Optional[Wishlist] = Relationship(back_populates="items")
    added_by: Optional[User] = Relationship(back_populates="items_added", sa_relationship_kwargs={"foreign_keys": "[Item.added_by_id]"})
    claimed_by: Optional[User] = Relationship(back_populates="items_claimed", sa_relationship_kwargs={"foreign_keys": "[Item.claimed_by_id]"})
    acquired_by: Optional[User] = Relationship(back_populates="items_acquired", sa_relationship_kwargs={"foreign_keys": "[Item.acquired_by_id]"})


load_dotenv(".env")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)
# SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

with Session(engine) as session:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # --- Create Users ---
    alice = User(name="Alice Johnson", email="alice@example.com", firebase_uid="123")
    bob = User(name="Bob Smith", email="bob@example.com", firebase_uid="456")
    emma = User(name="Emma Brown", email="emma@example.com", firebase_uid="789")

    session.add_all([alice, bob, emma])
    session.commit()

    # --- Create Wishlist (for Emma) ---
    wishlist = Wishlist(
        title="Emma’s Birthday 2025",
        recipient_name="Emma Brown",
        created_by_id=alice.id
    )
    session.add(wishlist)
    session.commit()

    # --- Link Users to Wishlist ---
    session.add_all([
        WishlistUserLink(wishlist_id=wishlist.id, user_id=alice.id, role="owner"),
        WishlistUserLink(wishlist_id=wishlist.id, user_id=emma.id, role="contributor"),
        WishlistUserLink(wishlist_id=wishlist.id, user_id=bob.id, role="contributor"),
    ])
    session.commit()

    # --- Add Items ---
    item1 = Item(
        wishlist_id=wishlist.id,
        added_by_id=bob.id,
        name="Wireless Headphones",
        description="Noise-cancelling, over-ear",
        url="https://example.com/headphones",
        claimed_by_id=alice.id,
        acquired_by_id=alice.id
    )

    item2 = Item(
        wishlist_id=wishlist.id,
        added_by_id=bob.id,
        name="Leather Journal",
        url="https://example.com/journal"
    )

    item3 = Item(
        wishlist_id=wishlist.id,
        added_by_id=emma.id,
        name="Comfy Socks",
        url="https://example.com/socks"
    )

    session.add_all([item1, item2, item3])
    session.commit()

app = FastAPI()

# cred = credentials.Certificate("../secrets/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)
firebase_admin.initialize_app(options={"projectId": "wishlists-64db1"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/user')
def get_current_user(
    request: Request,
    session: SessionDep
) -> User:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")

    token = auth_header.split(" ")[1]

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        firebase_uid = decoded_token["uid"]

        statement = select(User).where(User.firebase_uid == firebase_uid)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found in local database")

        return user

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
    
class UserUpdate(SQLModel):
    name: str | None
@app.put("/user")
def update_user(user_data: UserUpdate, session: SessionDep, current_user: User = Depends(get_current_user)):
    user_data = user_data.dict()
    for key, value in user_data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

class WishlistsReadWithUsers(SQLModel):
    id: int
    title: str
    recipient_name: str
    created_by_id: int
    created_at: datetime
    users: List[WishlistUserLink]

@app.get('/users/firebase-uid/{uid}')
def get_user_by_firebase_uid(uid: str, session: SessionDep):
    statement = select(User).where(User.firebase_uid == uid);
    results = session.exec(statement).first()

    return results

class UserCreate(SQLModel):
    email: str
    firebase_uid: str

@app.post("/users")
def create_user_from_firebase_user(user_data: UserCreate, session: SessionDep):
    user = User(**user_data.dict())

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

class WishlistCreate(SQLModel):
    title: str
    recipient_name: str

@app.post("/wishlists", response_model=WishlistsReadWithUsers)
def create_wishlist(wishlist_data: WishlistCreate, session: SessionDep, current_user: User = Depends(get_current_user)):
    wishlist = Wishlist(**wishlist_data.dict())
    wishlist.created_by_id = current_user.id

    session.add(wishlist)
    session.commit()
    session.refresh(wishlist)

    link = WishlistUserLink(
        wishlist_id=wishlist.id,
        user_id=wishlist.created_by_id,
        role="owner"
    )
    session.add(link)
    session.commit()

    statement = (
        select(Wishlist)
        .where(Wishlist.id == wishlist.id)
        .options(selectinload(Wishlist.users))  # Load users for response model
    )
    full_wishlist = session.exec(statement).first()

    return full_wishlist

class WishlistRead(SQLModel):
    id: int
    title: str

class UserReadWithWishlists(SQLModel):
    id: int
    name: str
    email: str
    wishlists_created: List[WishlistRead]

def get_user_with_wishlists(session: SessionDep, user_id: int) -> User:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.wishlists_created))  # Eager-load the relationship
    )
    result = session.exec(statement).first()
    return result

@app.get("/user/wishlists", response_model=List[WishlistsReadWithUsers])
def read_user_lists(session: SessionDep, current_user: User = Depends(get_current_user)):
    statement = (
        select(Wishlist)
        .join(WishlistUserLink)
        .where(WishlistUserLink.user_id == current_user.id)
        .options(selectinload(Wishlist.users))
    )

    results = session.exec(statement).all()

    return results

@app.get("/wishlists/{wishlist_id}")
def read_user_lists(wishlist_id: int, session: SessionDep):
    statement = (
        select(Wishlist)
        .where(Wishlist.id == wishlist_id)
    )

    results = session.exec(statement).first();

    return results


class UserWithRole(SQLModel):
    id: int
    name: str
    role: str
@app.get("/wishlists/{wishlist_id}/users", response_model=List[UserWithRole])
def read_wishlist_users(wishlist_id: int, session: SessionDep):
    statement = (
        select(User.id, User.name, WishlistUserLink.role)
        .join(WishlistUserLink)
        .where(WishlistUserLink.wishlist_id == wishlist_id)
    )

    results = session.exec(statement).all()

    return results

@app.post("/wishlists/{wishlist_id}/users")
def add_user_to_wishlist(wishlist_id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    link = WishlistUserLink(
      wishlist_id=wishlist_id,
      user_id=current_user.id,
      role="contributor"
      )

    session.add(link)
    session.commit()

    return

class ItemReadComplete(SQLModel):
    id: int
    wishlist_id: int
    name: str
    description: str | None
    url: str | None
    added_by: User | None
    claimed_by: User | None
    acquired_by: User | None

@app.get("/wishlists/{wishlist_id}/items", response_model=List[ItemReadComplete])
def read_wishlist_items(wishlist_id: int, session: SessionDep):
    statement = (
        select(Item)
        .where(Item.wishlist_id == wishlist_id)
        .where(Item.active == True)
        .options(
            selectinload(Item.added_by),
            selectinload(Item.claimed_by),
            selectinload(Item.acquired_by)
        )
    )

    results = session.exec(statement).all()

    return results

@app.get("/items/{item_id}", response_model=ItemReadComplete)
def read_wishlist_items(item_id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    statement = (
        select(Item)
        .where(Item.id == item_id)
    )
    item = session.exec(statement).one()

    if item.added_by_id == current_user.id:
      return item
    else:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current user did not add item")
    
class ItemCreate(SQLModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None

@app.post("/wishlists/{wishlist_id}/item", response_model=ItemReadComplete)
def add_item_to_wishlist(
    wishlist_id: int, 
    item_data: ItemCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    item = Item(
        **item_data.dict(),
        added_by_id=current_user.id,
        wishlist_id=wishlist_id
    )

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

class ItemEdit(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    active: Optional[bool] = None
@app.put("/items/{item_id}", response_model=ItemReadComplete)
def edit_wishlist_item(
    item_id: int,
    item_data: ItemEdit,
    session: SessionDep
):
    print(item_data)
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()

    item_data = item_data.dict()
    for key, value in item_data.items():
        if value is not None:
          setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.put("/items/{item_id}/claim", response_model=ItemReadComplete)
def claim_item(item_id: int, session: SessionDep, current_user=Depends(get_current_user)):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.claimed_by_id = current_user.id
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@app.put("/items/{item_id}/unclaim", response_model=ItemReadComplete)
def unclaim_item(item_id: int, session: SessionDep, current_user=Depends(get_current_user)):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.claimed_by_id = None
    session.add(item)
    session.commit()
    session.refresh(item)

    return item

@app.put("/items/{item_id}/acquire", response_model=ItemReadComplete)
def claim_item(item_id: int, session: SessionDep, current_user=Depends(get_current_user)):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.acquired_by_id = current_user.id
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@app.put("/items/{item_id}/unacquire", response_model=ItemReadComplete)
def unclaim_item(item_id: int, session: SessionDep):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.acquired_by_id = None
    session.add(item)
    session.commit()
    session.refresh(item)

    return item

@app.delete("/wishlists/{wishlist_id}/user")
def leave_wishlist(wishlist_id: int, user_id: int, session: Session = Depends(get_session), current_user=Depends(get_current_user)):
    statement = select(WishlistUserLink).where(
        WishlistUserLink.wishlist_id == wishlist_id,
        WishlistUserLink.user_id == current_user.id
    )

    link = session.exec(statement).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="User is not associated with this wishlist")

    session.delete(link)
    session.commit()

    return {"detail": "User successfully removed from wishlist"}

@app.get("/validate-invitation-id")
def validate_invitation_id(session: SessionDep, uuid: str = Query(...)):
    try:
        invitation_id = UUID(uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid invitation ID format")
    
    statement = select(Wishlist).where(Wishlist.invitation_id == invitation_id)
    result = session.exec(statement).one_or_none()

    if result:
        return result.id
    else:
        return False