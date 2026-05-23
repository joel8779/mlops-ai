from uuid import uuid4

import factory

from app.schemas.auth import AuthContext


class AuthContextFactory(factory.Factory):
    class Meta:
        model = AuthContext

    user_id = factory.LazyFunction(uuid4)
    organization_id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda number: f"recruiter{number}@example.com")
    roles = factory.LazyFunction(lambda: ["admin"])
