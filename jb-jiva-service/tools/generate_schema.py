from fastapi.openapi.utils import get_openapi

import json
from pathlib import Path

from jiva.user_api import user_app
from jiva.admin_api import admin_app


Path("./out/admin").mkdir(parents=True, exist_ok=True)

with open("out/admin/openapi.json", "w") as f:
    json.dump(
        get_openapi(
            title=admin_app.title,
            version=admin_app.version,
            openapi_version=admin_app.openapi_version,
            description=admin_app.description,
            routes=admin_app.routes,
            tags=admin_app.openapi_tags,
        ),
        f,
    )


Path("./out/user").mkdir(parents=True, exist_ok=True)

with open("out/user/openapi.json", "w") as f:
    json.dump(
        get_openapi(
            title=user_app.title,
            version=user_app.version,
            openapi_version=user_app.openapi_version,
            description=user_app.description,
            routes=user_app.routes,
            tags=user_app.openapi_tags,
        ),
        f,
    )
