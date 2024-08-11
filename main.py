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
from pydantic import BaseSettings
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import exc
import os

from modules import nftmint

class Settings(BaseSettings):
    
    postgres_prod: str
    postgres_dev: str
    collectionkey: str
    candy_program_id: str
    candy_guard_id: str
    candy_mint_acc: str
    mintsignature: str
    frontend_url: str
    sol_endpoint: str
    
    class Config:
        if os.getenv("ENV") == "production":
            env_file = None  # Use system env variables
        else:
            env_file = ".env"  # Use .env file for development
            

async def run_app(sol_endpoint: str, pubkeys: Dict, engine: AsyncEngine, lastsig: str) -> None:
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
            await nftmint.update_mint(settings.sol_endpoint, pubkeys, async_session, first_args)
        except:
            pass
        
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    if os.getenv("ENV") == "production":
        engine = create_async_engine(settings.postgres_prod)
    else:
        engine = create_async_engine(settings.postgres_dev)
        pubkeys = {
            "collection": settings.collectionkey, 
            "candyprogid": settings.candy_program_id,
            "candyguardgid": settings.candy_guard_id,
            "candymintacc": settings.candy_mint_acc,
               } 
    try:
        async with engine.begin() as conn:
            await conn.run_sync(NftMintBase.metadata.create_all)
        asyncio.create_task(run_app(settings.sol_endpoint, pubkeys, engine, settings.mintsignature))
    except:
        pass
    yield
    engine.dispose()

origins = [
    settings.frontend_url
]
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_all():
    if os.getenv("ENV") == "production":
        engine = create_async_engine(settings.postgres_prod)
    else:
        engine = create_async_engine(settings.postgres_dev)
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
    if os.getenv("ENV") == "production":
        engine = create_async_engine(settings.postgres_prod)
    else:
        engine = create_async_engine(settings.postgres_dev)
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
        except exc.SQLAlchemyError as e:
            print(type(e))
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint name "{name}"')
    return result

@app.get("/mint/from-address/{address}")
async def get_mint_by_name(address: str) -> Mint:
    if os.getenv("ENV") == "production":
        engine = create_async_engine(settings.postgres_prod)
    else:
        engine = create_async_engine(settings.postgres_dev)
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
        except exc.SQLAlchemyError as e:
            print(type(e))
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint name "{mint}"')
    return result

@app.get("/mint/newest")
async def get_mint_by_name() -> Mint:
    if os.getenv("ENV") == "production":
        engine = create_async_engine(settings.postgres_prod)
    else:
        engine = create_async_engine(settings.postgres_dev)
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
        except exc.SQLAlchemyError as e:
            print(type(e))
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint found"')
    return result

@app.get("/mint/oldest")
async def get_mint_by_name() -> Mint:
    if os.getenv("ENV") == "production":
        engine = create_async_engine(settings.postgres_prod)
    else:
        engine = create_async_engine(settings.postgres_dev)
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
        except exc.SQLAlchemyError as e:
            print(type(e))
    if not result:
        raise HTTPException(status_code=400, detail=f'No mint found"')
    return result
