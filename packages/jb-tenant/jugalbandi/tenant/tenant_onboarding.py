# import hashlib
# import random
# import string
# import time
import asyncio
from dotenv import load_dotenv
from .tenant_repository import TenantRepository
load_dotenv()


def get_inputs():
    tenant_name = input("Enter the Tenant's Name (once finished, press Enter): ")
    tenant_email = input("Enter the Tenant's Email ID (once finished, press Enter): ")
    tenant_api_key = input("Enter the Tenant's API Key (to skip, press Enter): ")
    tenant_weekly_quota = input("Enter the Tenant's Weekly Quota (to skip, press Enter): ")
    if tenant_weekly_quota == "":
        tenant_weekly_quota = 125
    return tenant_name, tenant_email, tenant_api_key, int(tenant_weekly_quota)


# def generate_api_key(length=32):
#     timestamp = str(time.time()).encode("utf-8")
#     random_data = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length)).encode("utf-8")
#     combined_data = timestamp + random_data
#     api_key = hashlib.sha256(combined_data).hexdigest()[:length]
#     return api_key


async def insert_into_tenant(
    tenant_name,
    tenant_email,
    tenant_api_key,
    tenant_weekly_quota
):
    tenant_repository = TenantRepository()
    await tenant_repository.insert_into_tenant(name=tenant_name,
                                               email_id=tenant_email,
                                               api_key=tenant_api_key,
                                               weekly_quota=tenant_weekly_quota)


if __name__ == "__main__":
    print("Give the required details for Tenant Onboarding")
    tenant_name, tenant_email, tenant_api_key, tenant_weekly_quota = get_inputs()
    # tenant_api_key = generate_api_key()
    asyncio.run(insert_into_tenant(tenant_name=tenant_name,
                                   tenant_email=tenant_email,
                                   tenant_api_key=tenant_api_key,
                                   tenant_weekly_quota=tenant_weekly_quota))
    print(f"Successfully created tenant {tenant_name} with API Key: {tenant_api_key}")
