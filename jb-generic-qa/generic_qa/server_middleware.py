from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jugalbandi.tenant import TenantRepository
from jugalbandi.core.errors import QuotaExceededException, UnAuthorisedException
from typing import Optional
import os


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
            tenant_repository: TenantRepository
    ):
        super().__init__(app)
        self.exception_endpoints = ["/", "/docs", "/openapi.json",
                                    "/source-document", "/response-feedback",
                                    "/get-balance-quota", "/query-using-voice-gpt3-5-turbo-4k"]
        self.tenant_repository = tenant_repository

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in self.exception_endpoints:
            api_key = request.query_params.get("api_key")
            balance_quota = await self.tenant_repository.get_balance_quota_from_api_key(api_key)
            if balance_quota is None:
                if os.environ["ALLOW_INVALID_API_KEY"] == "true":
                    pass
                else:
                    raise UnAuthorisedException("Invalid API key")
            else:
                await self.process_balance_quota(api_key=api_key, balance_quota=balance_quota)

        response = await call_next(request)
        return response

    async def process_balance_quota(self, api_key: Optional[str], balance_quota: int):
        if balance_quota > 0:
            await self.tenant_repository.update_balance_quota(api_key, balance_quota)
        else:
            raise QuotaExceededException("You have exceeded the quota limit")
