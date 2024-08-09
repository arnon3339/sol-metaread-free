from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

class Creator(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    verified: bool
    share: int
    create_at: datetime.datetime

class Mint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str 
    update_authority: str 
    mint: str 
    minter: str
    signature: str
    name: str
    symbol: str
    uri: str
    creators: Optional[List[Creator]]
    seller_fee_basis_points: int
    primary_sale_happened: bool
    is_mutable: bool
    edition_nonce: Optional[int] = None
    token_standard: Optional[str] = None
    collection_key: Optional[str] = None
    collection_verified: Optional[bool] = False
    uses_use_method: Optional[str] = None
    uses_remaining: Optional[int] = None
    uses_total: Optional[int] = None
    collection_details_label: Optional[str] = None
    collection_details_size:  Optional[int] = None
    programmable_config_label: Optional[str] = None
    programmable_config_rule_set: Optional[str] = None
    blocktime: int
    mint_at: datetime.datetime
    create_at: datetime.datetime
    last_update: datetime.datetime

