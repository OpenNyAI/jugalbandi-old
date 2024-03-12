import streamlit as st
from jugalbandi.tenant.tenant_repository import TenantRepository

state = st.session_state
if "email" not in state:
    state["email"] = ""

url = "https://api.jugalbandi.ai/docs"
height = 1000
width = "100%"
tenant_repository = TenantRepository()
tenant_details = tenant_repository.get_tenant_details(state["email"])


with st.container():
    st.write("## Swagger Documentation")
    st.write("---")
    if tenant_details:
        st.write(f"#### API Key: {tenant_details[2]}")
        st.write(f"#### API Quota: {tenant_details[3]}")
    st.write("")
    # st.write(
    #     f'<iframe src="{url}" width="{width}" height="{height}px"></iframe>',
    #     unsafe_allow_html=True,
    #     width=1000,
    # )
    st.components.v1.html(
        f'<iframe src="{url}" width="{width}" height="{height}"></iframe>',
        height=height,
        width=1000,
    )
