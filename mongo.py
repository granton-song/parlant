from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, Awaitable

from lagom import Container
from parlant.adapters.db.mongo_db import MongoDocumentDatabase
from parlant.core.agents import AgentDocumentStore, AgentStore
from parlant.core.context_variables import (
    ContextVariableDocumentStore,
    ContextVariableStore,
)
from parlant.core.customers import CustomerDocumentStore, CustomerStore
from parlant.core.evaluations import EvaluationDocumentStore, EvaluationStore
from parlant.core.guideline_tool_associations import (
    GuidelineToolAssociationDocumentStore,
    GuidelineToolAssociationStore,
)
from parlant.core.guidelines import GuidelineDocumentStore, GuidelineStore
from parlant.core.loggers import Logger
from parlant.core.persistence.document_database import DocumentDatabase
from parlant.core.relationships import RelationshipDocumentStore, RelationshipStore
from parlant.core.sessions import SessionDocumentStore, SessionStore
from parlant.core.tags import TagDocumentStore, TagStore
from pymongo.asynchronous.mongo_client import AsyncMongoClient

EXIT_STACK = AsyncExitStack()


@asynccontextmanager
async def make_mongo_client(host: str):
    client = AsyncMongoClient[Any](host)
    try:
        yield client
    finally:
        if client:
            await client.close()


async def configure_module(container: Container) -> Container:
    mongo_client = await EXIT_STACK.enter_async_context(make_mongo_client("mongodb"))

    def make_mongodb(database_name: str) -> Awaitable[DocumentDatabase]:
        return EXIT_STACK.enter_async_context(
            MongoDocumentDatabase(
                mongo_client=mongo_client, database_name=database_name, logger=container[Logger]
            )
        )

    for interface, implementation, db_name in [
        (AgentStore, AgentDocumentStore, "agents"),
        (ContextVariableStore, ContextVariableDocumentStore, "context_variables"),
        (CustomerStore, CustomerDocumentStore, "customers"),
        (EvaluationStore, EvaluationDocumentStore, "evaluations"),
        (TagStore, TagDocumentStore, "tags"),
        (GuidelineStore, GuidelineDocumentStore, "guidelines"),
        (
            GuidelineToolAssociationStore,
            GuidelineToolAssociationDocumentStore,
            "guideline_tool_associations",
        ),
        (RelationshipStore, RelationshipDocumentStore, "relationships"),
        (SessionStore, SessionDocumentStore, "sessions"),
    ]:
        container[interface] = await EXIT_STACK.enter_async_context(
            implementation(await make_mongodb(db_name))  # type: ignore
        )

    return container


async def initialize_module(container: Container) -> None:
    pass


async def shutdown_module() -> None:
    pass
