# This module connects to an SQL database.
# Changes are required to switch from SQLModel to ODMantic (MongoDB).
# This module manages CRUD (Create, Read, Update, Delete) operations for items, 
# ensuring proper user authentication and authorization.


from typing import Any
from fastapi import APIRouter, HTTPException
from odmantic import AIOEngine, ObjectId

from app.api.deps import CurrentUser, EngineDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter()

@router.get("/", response_model=ItemsPublic)
async def read_items(
     engine: EngineDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
   
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count = await engine.count(Item)
        items = await engine.find(Item, skip=skip, limit=limit)
    else:
        count = await engine.count(Item, Item.owner_id == ObjectId(current_user.id))
        items = await engine.find(Item, Item.owner_id == ObjectId(current_user.id), skip=skip, limit=limit)
    return ItemsPublic(data=items, count=count)



@router.get("/{id}", response_model=ItemPublic)
async def read_item(engine: EngineDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get item by ID.
    """
    item = await engine.find_one(Item, Item.id == ObjectId(id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
async def create_item(
    *, engine: EngineDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = Item(**item_in.dict(), owner_id=ObjectId(current_user.id))
    await engine.save(item)
    item = await engine.find_one(Item, Item.id == item.id)
    return item
    


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    *, engine: EngineDep, current_user: CurrentUser, id: int, item_in: ItemUpdate
) -> Any:
    """
    Update an item.
    """
    item = await engine.find_one(Item, Item.id == ObjectId(id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
    await engine.save(item)
    item = await engine.find_one(Item, Item.id == item.id)
    return item


@router.delete("/{id}")
async def delete_item(engine: EngineDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an item.
    """
    
    item = await engine.find_one(Item, Item.id == ObjectId(id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    await engine.delete(item)
    return Message(message="Item deleted successfully")
