import asyncio
from dotenv import load_dotenv
from .tenant_repository import TenantRepository
load_dotenv()


def get_tenant_update_inputs():
    api_key = input("Enter the Tenant's API Key (once finished, press Enter): ")
    tenant_name = input("Enter the Tenant's New Name (once finished, press Enter): ")
    tenant_email = input("Enter the Tenant's New Email ID (once finished, press Enter): ")
    tenant_weekly_quota = input("Enter the Tenant's New Weekly Quota (to skip, press Enter): ")
    if tenant_weekly_quota == "":
        tenant_weekly_quota = 200
    return api_key, tenant_name, tenant_email, int(tenant_weekly_quota)


async def update_tenant_information(
    tenant_name,
    tenant_email,
    tenant_api_key,
    tenant_weekly_quota
):
    tenant_repository = TenantRepository()
    await tenant_repository.update_tenant_information(name=tenant_name,
                                                      email_id=tenant_email,
                                                      api_key=tenant_api_key,
                                                      weekly_quota=tenant_weekly_quota)


async def reset_balance_quota_for_tenant(tenant_api_key):
    tenant_repository = TenantRepository()
    await tenant_repository.reset_balance_quota_for_tenant(api_key=tenant_api_key)


if __name__ == "__main__":
    print("\nType 1 for 'Reset Balance Quota for Tenant'\nType 2 for 'Update Tenant Information'")
    number = int(input("Enter your choice: "))
    if number == 1:
        tenant_api_key = input("Enter the Tenant's API Key (once finished, press Enter): ")
        asyncio.run(reset_balance_quota_for_tenant(tenant_api_key=tenant_api_key))
        print(f"Successfully weekly quota is reset for the tenant with API KEY: {tenant_api_key}")
    elif number == 2:
        print("Give the required details for Tenant Information updation")
        tenant_api_key, tenant_name, tenant_email, tenant_weekly_quota = get_tenant_update_inputs()
        asyncio.run(update_tenant_information(tenant_name=tenant_name,
                                              tenant_email=tenant_email,
                                              tenant_api_key=tenant_api_key,
                                              tenant_weekly_quota=tenant_weekly_quota))
        print(f"Successfully updated tenant information for tenant with API Key: {tenant_api_key}")
