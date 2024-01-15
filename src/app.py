from contextlib import contextmanager
from time import sleep
from uuid import uuid4
import strawberry
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.permission import BasePermission
import asyncio
import logbook
import fastapi


class GQLContext(BaseContext):
    def __init__(self):
        super().__init__()
        self.telemetry = TelemetryContext()


class TrackingSchema(strawberry.Schema):
    def execute_sync(self, *args, **kwargs):
        context = kwargs.get("context_value")
        if context:
            with context.telemetry.with_telemetry():
                return super().execute_sync(*args, **kwargs)
        else:
            return super().execute_sync(*args, **kwargs)

    async def execute(self, *args, **kwargs):
        context = kwargs.get("context_value")
        if context:
            with context.telemetry.with_telemetry():
                return await super().execute(*args, **kwargs)
        else:
            return await super().execute(*args, **kwargs)


class IsAuthorized(BasePermission):
    async def has_permission(self, source, info, **kwargs):
        await asyncio.sleep(1)
        return True


class TelemetryContext:
    def __init__(self) -> None:
        self._context_map = {"request_id": uuid4()}

    @contextmanager
    def with_telemetry(self):
        with logbook.Processor(self._inject_logging_context):
            yield

    def _inject_logging_context(self, record: logbook.LogRecord):
        record.extra.update(self._context_map)


async def get_context():
    return GQLContext()


@strawberry.type
class Mutation:  # noqa: D
    @strawberry.mutation(permission_classes=[IsAuthorized])
    def mutation(self, info) -> bool:
        sleep(1)
        return True


@strawberry.type
class Query:  # noqa: D
    @strawberry.mutation(permission_classes=[IsAuthorized])
    def query(self, info) -> bool:
        sleep(1)
        return True


app = fastapi.FastAPI()

schema = TrackingSchema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
