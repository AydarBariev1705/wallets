import uuid
from fastapi import APIRouter


router = APIRouter(
    prefix="/api/v1/wallets",
    tags=["wallets"],
    )

@router.get("/")
async def create_wallet():
    uuid_v4 = uuid.uuid4()
    return {"New Wallet Created": uuid_v4,
            "Balance": 0, }
 