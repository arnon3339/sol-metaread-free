from modules.models.nftmint import NftMint, MintCreator
from modules.metaplex import Metadata
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import List

import datetime

async def upload_metas(async_session: async_sessionmaker[AsyncSession], 
        metadatas: List[Metadata]) -> None:
    mint_data = []
    creator_data = []
    for d in metadatas:
        mint_data.append(
                { 
                    "key": d.key,
                    "update_authority": str(d.update_authority),
                    "mint": str(d.mint),
                    "minter": str(d.minter),
                    "signature": str(d.signature),
                    "name": d.name,
                    "symbol": d.symbol,
                    "uri": d.uri,
                    "seller_fee_basis_points": d.seller_fee_basis_points,
                    "primary_sale_happened": d.primary_sale_happened,
                    "is_mutable": d.is_mutable,
                    "edition_nonce": d.edition_nonce if d.edition_nonce else None,
                    "token_standard": d.token_standard,
                    "collection_key": str(d.collection.key) if d.collection else None,
                    "collection_verified": d.collection.verified if d.collection else None,
                    "uses_use_method": str(d.uses.use_method) if d.uses else None,
                    "uses_remaining": d.uses.remaining if d.uses else None,
                    "uses_total": d.uses.total if d.uses else None,
                    "collection_details_label": d.collection_details.label if d.collection_details else None,
                    "collection_details_size": d.collection_details.size if d.collection_details else None,
                    "programmable_config_label": d.programmable_config.label if d.programmable_config else None,
                    "programmable_config_rule_set": d.programmable_config.rule_set if d.programmable_config else None,
                    "blocktime": d.blocktime,
                    "mint_at": datetime.datetime.utcfromtimestamp(d.blocktime),
                    "last_update": datetime.datetime.now()
                } 
            )
        creator_mint = []
        for c_i, c in enumerate(d.creators):
            creator_mint.append(
                {"address": str(c.address), "verified": c.verified, "share": c.share, "mint_key": str(d.mint), "creator_order": c_i}
                )
        creator_data.append(creator_mint)
    async with async_session() as session:
        for mdata_i, mdata in enumerate(mint_data):
            rows = await session.scalars(select(NftMint).where(NftMint.mint == mdata["mint"]))
            found_mint = rows.first()
            if not found_mint:
                stmt_mint = insert(NftMint).returning(NftMint.id)
                result = await session.scalars(stmt_mint, [mdata])
                stmt_creator = insert(MintCreator)
                await session.execute(stmt_creator, creator_data[mdata_i])
                print(f"{result.all()[0]} -> {mdata['mint']}")
        await session.commit()
