import datetime

from sqlalchemy import ForeignKey, DateTime, func, TIMESTAMP, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from typing import List, Optional

#NftMintBase = declarative_base()

class NftMintBase(DeclarativeBase):
    type_annotation_map = {
            datetime.datetime: TIMESTAMP(timezone=True)
    }

class MintCreator(NftMintBase):
    __tablename__ = "creator"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str]
    verified: Mapped[bool]
    share: Mapped[int]
    mint_key: Mapped[str] = mapped_column(ForeignKey("mint.mint"))
    creator_order: Mapped[int]
    create_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    mint: Mapped["NftMint"] = relationship(back_populates="creators", lazy="selectin")

class NftMint(NftMintBase):
    __tablename__ = "mint"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str]
    update_authority: Mapped[str]
    mint: Mapped[str] = mapped_column(unique=True)
    minter: Mapped[str]
    signature: Mapped[str]
    name: Mapped[str] = mapped_column(unique=True)
    symbol: Mapped[str]
    uri: Mapped[str] = mapped_column(unique=True)
    seller_fee_basis_points: Mapped[int]
    primary_sale_happened: Mapped[int]
    is_mutable: Mapped[bool]
    edition_nonce: Mapped[Optional[int]]
    token_standard: Mapped[Optional[str]]
    collection_key: Mapped[Optional[str]]
    collection_verified: Mapped[Optional[bool]]
    uses_use_method: Mapped[Optional[str]]
    uses_remaining: Mapped[Optional[int]]
    uses_total: Mapped[Optional[int]]
    collection_details_label: Mapped[Optional[str]]
    collection_details_size: Mapped[Optional[int]]
    programmable_config_label: Mapped[Optional[str]]
    programmable_config_rule_set: Mapped[Optional[str]]
    blocktime: Mapped[int]
    mint_at: Mapped[datetime.datetime]
    create_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    last_update: Mapped[datetime.datetime]

    creators: Mapped[Optional[List["MintCreator"]]] = relationship(back_populates="mint", lazy="selectin")

