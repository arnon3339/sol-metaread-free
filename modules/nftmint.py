import asyncio
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import Transaction
from modules.metaplex import get_metadata
from typing import Dict, List
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from modules import metadb
from modules.metaplex import Metadata
import json
from sqlalchemy import exc

async def update_mint(endpoint: str, pubkeys: Dict, async_session: async_sessionmaker[AsyncSession],
        first_args: Dict) -> None:
    while True:
        if not first_args["running"]:
            first_args["running"] = True
            try:
                async with AsyncClient(endpoint) as client:
                    res = await client.is_connected()
                    collection_data = await client.get_signatures_for_address(
                            Pubkey.from_string(pubkeys["collection"]),
                            commitment="finalized",
                            until=Signature.from_string(first_args["lastsignature"])
                            )
                    collection_data_json = json.loads(collection_data.to_json())
                    signatures = [d["signature"] for d in collection_data_json['result']]
                    nft_metas = await collect_nfts(client, signatures, pubkeys)
                    if nft_metas:
                        await metadb.upload_metas(async_session, nft_metas)
            except exc.SQLAlchemyError as e:
                print(type(e))
            await asyncio.sleep(5)
            first_args["running"] = False

async def collect_nfts(client: AsyncClient, signatures: List[str], pubkeys: List[str]) -> List[Metadata]:
    nft_metas = []
    for i, signature in enumerate(signatures):
        try:
            tx = await client.get_transaction(Signature.from_string(signature), encoding="jsonParsed", commitment="finalized", 
                max_supported_transaction_version=3)
            json_data = json.loads(tx.value.transaction.to_json())
            #instructions = json_data['meta']['innerInstructions'][0]['instructions']
            instructions = json_data['transaction']['message']['instructions']
            #print(f"{i}. {instructions}")
            mint_program = instructions[1]
            nft_mint = ""
            nft_minter = ""
            if "Guard" in mint_program['programId']:
                nft_mint = mint_program['accounts'][6]
                nft_minter = mint_program['accounts'][5]
            elif "Cndy" in mint_program['programId']:
                nft_mint = mint_program['accounts'][5]
                nft_minter = mint_program['accounts'][4]
            else:
                continue
            tx_norm = await client.get_transaction(Signature.from_string(signature), commitment="finalized",
                    max_supported_transaction_version=3)
            blocktime = tx_norm.value.block_time
            meta_data = await get_metadata(client, nft_mint, nft_minter, signature, blocktime)
            nft_metas.append(meta_data)
        except exc.SQLAlchemyError as e:
            print(type(e))
    return nft_metas 
