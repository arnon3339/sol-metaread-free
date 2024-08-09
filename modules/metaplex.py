from solders.pubkey import Pubkey
from solders.signature import Signature 
import base64
import json
import struct
from meta_read.meta_read import read_meta
import modules
from typing import List, Dict
from dataclasses import dataclass

METADATA_PROGRAM_ID = Pubkey.from_string('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s')
SYSTEM_PROGRAM_ID = Pubkey.from_string('11111111111111111111111111111111')
SYSVAR_RENT_PUBKEY = Pubkey.from_string('SysvarRent111111111111111111111111111111111') 
ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID = Pubkey.from_string('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')
TOKEN_PROGRAM_ID = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')

@dataclass
class Creator:
    address: Pubkey
    verified: bool
    share: int

@dataclass
class Collection:
    key: Pubkey
    verified: bool

@dataclass
class Uses:
    use_method: str
    remaining: int
    total: int

@dataclass
class CollectionDetails:
    label: str
    size: int

@dataclass
class ProgrammableConfig:
    label: str
    rule_set: Pubkey

@dataclass
class Metadata:
    key: str 
    update_authority: Pubkey 
    mint: Pubkey
    minter: Pubkey
    signature: Signature
    name: str
    symbol: str
    uri: str
    seller_fee_basis_points: int 
    creators: List[Creator]
    primary_sale_happened: bool
    is_mutable: bool
    edition_nonce: int
    token_standard: str
    collection: Collection
    uses: Uses
    collection_details: CollectionDetails
    programmable_config: ProgrammableConfig
    blocktime: int

def get_metadata_account(mint_key) -> Pubkey:
    return Pubkey.find_program_address([b'metadata', bytes(METADATA_PROGRAM_ID), bytes(Pubkey.from_string(mint_key))],
            METADATA_PROGRAM_ID)[0] 

async def get_metadata(client, mint_key, minter_key, signature, blocktime) -> Metadata:
    metadata_account = get_metadata_account(mint_key)
    client_data = await client.get_account_info_json_parsed(metadata_account, commitment="finalized")
    json_data = json.loads(client_data.to_json())
    data = json_data['result']['value']['data'][0]
    meta_bytes = base64.b64decode(data)
    rust_metadata = read_meta(meta_bytes)
    creators = [Creator(Pubkey.from_string(creator.address), creator.verified, creator.share) for creator in rust_metadata.creators]
    edition_nonce = rust_metadata.edition_nonce
    token_standard = rust_metadata.token_standard
    collection = Collection(Pubkey.from_string(rust_metadata.collection["key"]), True if rust_metadata.collection["verified"] == "true" else False)\
            if rust_metadata.collection else None
    uses = Uses(rust_metadata.uses["use_method"], rust_metadata.collection["remaining"], rust_metadata.collection["total"])\
            if rust_metadata.uses else None
    collection_details = CollectionDetails(rust_metadata.collecton_details["label"], rust_metadata.collection_details["size"])\
            if rust_metadata.collection_details else None
    programmable_config = CollectionDetails(rust_metadata.collecton_details["label"], Pubkey.from_string(rust_metadata.programmable_config["rule_set"]))\
            if rust_metadata.programmable_config else None
    meta_data = Metadata(
            rust_metadata.key.replace('\x00', ''),
            Pubkey.from_string(rust_metadata.update_authority),
            Pubkey.from_string(rust_metadata.mint),
            Pubkey.from_string(minter_key),
            Signature.from_string(signature),
            rust_metadata.name.replace('\x00', ''),
            rust_metadata.symbol.replace('\x00', ''),
            rust_metadata.uri.replace('\x00', ''),
            int(rust_metadata.seller_fee_basis_points),
            creators,
            rust_metadata.primary_sale_happened,
            rust_metadata.is_mutable,
            int(edition_nonce),
            token_standard,
            collection,
            uses,
            collection_details,
            programmable_config,
            blocktime
            )
    return meta_data
