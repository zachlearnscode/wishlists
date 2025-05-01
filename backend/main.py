from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, SQLModel, create_engine, Relationship, Session, select
from sqlalchemy.orm import selectinload
from typing import Optional, List, Annotated, Literal
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4, UUID


# --------- USER ---------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    firebase_uid: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

    wishlist: Optional[Wishlist] = Relationship(back_populates="items")
    added_by: Optional[User] = Relationship(back_populates="items_added", sa_relationship_kwargs={"foreign_keys": "[Item.added_by_id]"})
    claimed_by: Optional[User] = Relationship(back_populates="items_claimed", sa_relationship_kwargs={"foreign_keys": "[Item.added_by_id]"})
    acquired_by: Optional[User] = Relationship(back_populates="items_acquired", sa_relationship_kwargs={"foreign_keys": "[Item.acquired_by_id]"})



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


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/users/firebase-uid/{uid}')
def get_user_by_firebase_uid(uid: str, session: SessionDep):
    statement = select(User).where(User.firebase_uid == uid);
    results = session.exec(statement).first()

    return results

class UserCreate(SQLModel):
    email: str
    firebase_uid: str
    name: str

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
    created_by_id: int

@app.post("/wishlists")
def create_wishlist(wishlist_data: WishlistCreate, session: SessionDep):
    wishlist = Wishlist(**wishlist_data.dict())

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

    return wishlist

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

class WishlistsReadWithUsers(SQLModel):
    id: int
    title: str
    recipient_name: str
    created_by_id: int
    created_at: datetime
    users: List[WishlistUserLink]

@app.get("/users/{user_id}/wishlists", response_model=List[WishlistsReadWithUsers])
def read_user_lists(user_id: int, session: SessionDep):
    statement = (
        select(Wishlist)
        .join(WishlistUserLink)
        .where(WishlistUserLink.user_id == user_id)
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

@app.get("/wishlists/{wishlist_id}/items")
def read_wishlist_items(wishlist_id: int, session: SessionDep):
    statement = (
        select(Item)
        .where(Item.wishlist_id == wishlist_id)
    )

    results = session.exec(statement).all()

    return results

@app.get("/items/{item_id}")
def read_wishlist_items(item_id: int, session: SessionDep):
    statement = (
        select(Item)
        .where(Item.id == item_id)
    )

    results = session.exec(statement).one()

    return results

class ItemCreate(SQLModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    added_by_id: int

@app.post("/wishlists/{wishlist_id}/item")
def add_item_to_wishlist(
    wishlist_id: int, 
    item_data: ItemCreate, 
    session: SessionDep
):
    item = Item(
        **item_data.dict(),
        wishlist_id=wishlist_id
    )

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

class ItemEdit(SQLModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
@app.put("/items/{item_id}")
def edit_wishlist_item(
    item_id: int,
    item_data: ItemEdit,
    session: SessionDep
):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()

    item_data = item_data.dict()
    for key, value in item_data.items():
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.put("/items/{item_id}/claim")
def claim_item(item_id: int, session: SessionDep):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.claimed_by_id = 3
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@app.put("/items/{item_id}/unclaim")
def unclaim_item(item_id: int, session: SessionDep):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.claimed_by_id = None
    session.add(item)
    session.commit()
    session.refresh(item)

    return item

@app.put("/items/{item_id}/acquire")
def claim_item(item_id: int, session: SessionDep):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.acquired_by_id = 3
    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@app.put("/items/{item_id}/unacquire")
def unclaim_item(item_id: int, session: SessionDep):
    statement = select(Item).where(Item.id == item_id)
    results = session.exec(statement)

    item = results.one()
    item.acquired_by_id = None
    session.add(item)
    session.commit()
    session.refresh(item)

    return item

@app.delete("/wishlists/{wishlist_id}/users/{user_id}")
def leave_wishlist(wishlist_id: int, user_id: int, session: Session = Depends(get_session)):
    statement = select(WishlistUserLink).where(
        WishlistUserLink.wishlist_id == wishlist_id,
        WishlistUserLink.user_id == user_id
    )

    link = session.exec(statement).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="User is not associated with this wishlist")

    session.delete(link)
    session.commit()

    return {"detail": "User successfully removed from wishlist"}