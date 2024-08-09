import asyncio
from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from modules.models.nftmint import NftMintBase, NftMint
from modules.models.resmodel import Mint, Creator 
from contextlib import asynccontextmanager
from typing import Dict, List
from dotenv import dotenv_values 

from modules import nftmint

async def run_app(endpoint: str, pubkeys: Dict, engine: AsyncEngine, lastsig: str) -> None:
    first_args = {"lastsignature": lastsig, 
            "running": False}
    if not first_args["running"]:
        try:
            async_session = async_sessionmaker(engine, expire_on_commit=False)
            async with async_session() as session:
                stmt = select(NftMint.signature).order_by(NftMint.blocktime.desc())
                result = await session.scalars(stmt)
                latest_signature = result.first()
                if latest_signature:
                    first_args["lastsignature"] = latest_signature
            await nftmint.update_mint(endpoint, pubkeys, async_session, first_args)
        except:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    engine = None
    endpoint = ""
    pubkey = {}
    config = dotenv_values("../env.local")
    if config["ENV"] == "PRODUCTION":
        engine = create_async_engine(config["POSTGRES_PROD"])
    else:
        engine = create_async_engine(config["POSTGRES_DEV"])
        endpoint = config["ENDPOINT"]
        pubkeys = {
            "collection": config["COLLECTIONKEY"], 
            "candyprogid": config["CANDY_PROGRAM_ID"],
            "candyguardgid": config["CANDY_GUARD_ID"],
            "candymintacc": config["CANDY_MINT_ACC"],
               } 
    try:
        async with engine.begin() as conn:
            await conn.run_sync(NftMintBase.metadata.create_all)
        asyncio.create_task(run_app(endpoint, pubkeys, engine, config["MINTSIGNATURE"]))
    except:
        pass
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_all():
    engine = None
    config = dotenv_values(".env")
    if config["ENV"] == "PRODUCTION":
        engine = create_async_engine(config["POSTGRES_PROD"])
    else:
        engine = create_async_engine(config["POSTGRES_DEV"])
    results = []
    try:
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            stmt = select(NftMint)
            res = await session.scalars(stmt)
            mints = res.all()
            for mint in mints:
                new_creators = [
                                {
                                    column.name: getattr(ins, column.name)\
                                        for column in ins.__table__.columns if column.name != '_sa_instance_state'
                                }\
                                for ins in mint.creators
                            ]
                creators = [Creator.model_validate(c) for c in new_creators]
                mint_data = Mint.model_validate(mint)
                mint_data.creators = creators
                results.append(mint_data)
    except:
        raise HTTPException(status_code=400, detail="Connection fail")
    return results

@app.get("/mint/from-name/{name}")
async def get_mint_by_name(name: str):
    engine = None
    config = dotenv_values(".env")
    if config["ENV"] == "PRODUCTION":
        engine = create_async_engine(config["POSTGRES_PROD"])
    else:
        engine = create_async_engine(config["POSTGRES_DEV"])
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    result = None
    async with async_session() as session:
        try:
            stmt = select(NftMint).where(NftMint.name == name)
            res = await session.scalars(stmt)
            mint = res.first()
            new_creators = [
                            {
                                column.name: getattr(ins, column.name)\
                                    for column in ins.__table__.columns if column.name != '_sa_instance_state'
                            }\
                            for ins in mint.creators
                        ]
            creators = [Creator.model_validate(c) for c in new_creators]
            result = Mint.model_validate(mint)
            result.creators = creators
        except:
            pass
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint name "{name}"')
    return result

@app.get("/mint/from-address/{address}")
async def get_mint_by_name(address: str) -> Mint:
    engine = None
    config = dotenv_values(".env")
    if config["ENV"] == "PRODUCTION":
        engine = create_async_engine(config["POSTGRES_PROD"])
    else:
        engine = create_async_engine(config["POSTGRES_DEV"])
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    result = None
    async with async_session() as session:
        try:
            stmt = select(NftMint).where(NftMint.mint == address)
            res = await session.scalars(stmt)
            mint = res.first()
            new_creators = [
                            {
                                column.name: getattr(ins, column.name)\
                                    for column in ins.__table__.columns if column.name != '_sa_instance_state'
                            }\
                            for ins in mint.creators
                        ]
            creators = [Creator.model_validate(c) for c in new_creators]
            result = Mint.model_validate(mint)
            result.creators = creators
        except:
            pass
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint name "{mint}"')
    return result

@app.get("/mint/newest")
async def get_mint_by_name() -> Mint:
    engine = None
    config = dotenv_values(".env")
    if config["ENV"] == "PRODUCTION":
        engine = create_async_engine(config["POSTGRES_PROD"])
    else:
        engine = create_async_engine(config["POSTGRES_DEV"])
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    result = None
    async with async_session() as session:
        try:
            stmt = select(NftMint).order_by(NftMint.id.desc())
            res = await session.scalars(stmt)
            mint = res.first()
            new_creators = [
                            {
                                column.name: getattr(ins, column.name)\
                                    for column in ins.__table__.columns if column.name != '_sa_instance_state'
                            }\
                            for ins in mint.creators
                        ]
            creators = [Creator.model_validate(c) for c in new_creators]
            result = Mint.model_validate(mint)
            result.creators = creators
        except:
            pass
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint found"')
    return result

@app.get("/mint/oldest")
async def get_mint_by_name() -> Mint:
    engine = None
    config = dotenv_values(".env")
    if config["ENV"] == "PRODUCTION":
        engine = create_async_engine(config["POSTGRES_PROD"])
    else:
        engine = create_async_engine(config["POSTGRES_DEV"])
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    result = None
    async with async_session() as session:
        try:
            stmt = select(NftMint).order_by(NftMint.id.asc())
            res = await session.scalars(stmt)
            mint = res.first()
            new_creators = [
                            {
                                column.name: getattr(ins, column.name)\
                                    for column in ins.__table__.columns if column.name != '_sa_instance_state'
                            }\
                            for ins in mint.creators
                        ]
            creators = [Creator.model_validate(c) for c in new_creators]
            result = Mint.model_validate(mint)
            result.creators = creators
        except:
            pass
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint found"')
    return result
