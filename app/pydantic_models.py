from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List

ALLOWED_ASSETS = ['BTC', 'ETH', 'GOLD']

class Subscription(BaseModel):
    asset_name: str
    target_price: float

    @field_validator('asset_name')
    #@classmethod
    def check_allowed_assets(cls, v: str) -> str:
        asset = v.upper()
        #print("check_allowed_assets")
        if asset not in ALLOWED_ASSETS:
            raise ValueError(f"Asset {asset} is not available!")   
        return asset

    @field_validator('target_price')
    #@classmethod
    def prevent_zero_target(cls, p: float) -> float:
        #print("check target")
        if p <= 0:
            raise ValueError(f"Price is wrong!")
        return p

class User(BaseModel):
    login: str = Field(..., min_length=3, max_length=15)
    subscriptions: List[Subscription] = Field(default=[], max_length=3)


