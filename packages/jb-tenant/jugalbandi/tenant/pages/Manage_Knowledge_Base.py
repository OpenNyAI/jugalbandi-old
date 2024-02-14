import re
import uuid

import streamlit as st
from helper import country_phone_code_mapping
from tenant_repository import TenantRepository

tenant_repository = TenantRepository()
state = st.session_state
country_list = list(country_phone_code_mapping.keys())
st.set_page_config(
    page_title="Jugalbandi",
    page_icon="😎",
    layout="wide",
)
if "bot_data" not in state:
    state["bot_data"] = {}
if "email" not in state:
    state["email"] = ""


def get_key_by_value(dictionary, search_value):
    for key, value in dictionary.items():
        if value == search_value:
            return key
    return None


def validate_phone_number(mobile_number):
    mobile_format = r"^\+?\d{1,3}[-. ]?\d{3,14}$"
    if re.match(mobile_format, mobile_number):
        return True
    else:
        return False


def add_phone_number(key):
    state["bot_data"][key].append(
        {
            "phone_number": "",
            "base_key": str(uuid.uuid4()),
            "knowledge_base_name": state["bot_data"][key][0]["knowledge_base_name"],
            "country_code": "",
        }
    )


def _remove_phone_number(bot, base_key):
    for item in state["bot_data"][bot]:
        if item.get("base_key") == base_key:
            state["bot_data"][bot].remove(item)


def init_state():
    if state["bot_data"] == {}:
        print("ONCE INSIDE STATE")
        data = tenant_repository.get_tenant_document_details_from_email_id(
            state["email"]
        )
        bot_data = {}
        for d in data:
            base_key = str(uuid.uuid4())
            if d[0] not in bot_data:
                bot_data[d[0]] = []
            bot_data[d[0]].append(
                {
                    "base_key": base_key,
                    "phone_number": d[1][len(d[3]) :],
                    "knowledge_base_name": d[2],
                    "country_code": d[3],
                }
            )
        state["bot_data"] = bot_data


def update_data(bot):
    with st.spinner("Updation in progess"):
        tenant_details = tenant_repository.get_tenant_details(state["email"])
        tenant_repository.update_tenant_bot_details(
            document_uuid=bot,
            tenant_api_key=tenant_details[2],
            updated_bot_details=state["bot_data"][bot],
        )
    st.toast("Bot updated successfully!", icon="✅")


def remove_bot(bot):
    with st.spinner("Deletion in progress"):
        tenant_repository.delete_tenant_bot_details(document_uuid=bot)
        del state["bot_data"][bot]
    st.toast("Bot deleted successfully!", icon="✅")


def main():
    init_state()
    st.title("My Knowledge Library")
    for bot in state["bot_data"]:
        data = state["bot_data"][bot]
        print(data[0]["knowledge_base_name"], len(data))
        with st.expander(data[0]["knowledge_base_name"]):
            for i in range(len(data)):
                row_columns = st.columns((3, 2, 1))
                base_key = data[i]["base_key"]
                with row_columns[0]:
                    default_value = get_key_by_value(
                        country_phone_code_mapping, data[i]["country_code"]
                    )
                    if default_value is None:
                        default_value = "India"
                    selected_country = st.selectbox(
                        label="Select the country",
                        key=base_key + "country_select",
                        options=tuple(country_phone_code_mapping.keys()),
                        index=country_list.index(default_value),
                    )
                with row_columns[1]:
                    phone_number = st.text_input(
                        label="Phone number",
                        value=data[i]["phone_number"],
                        key=base_key + "phone_number_input",
                    )
                with row_columns[2]:
                    st.markdown(
                        """
                        <style>
                            button[kind="secondary"] {
                                margin-top: 0.80em;
                            }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.button(
                        label="Remove",
                        key=base_key + "remove_button",
                        on_click=_remove_phone_number,
                        args=(
                            bot,
                            base_key,
                        ),
                        type="secondary",
                    )
                    if phone_number and not validate_phone_number(phone_number):
                        st.error(
                            "Invalid phone number. Please enter a valid number without spaces or special characters."
                        )
                state["bot_data"][bot][i]["country_code"] = country_phone_code_mapping[
                    selected_country
                ]
                state["bot_data"][bot][i]["phone_number"] = phone_number

            st.button(
                label="Add User",
                key=data[i]["phone_number"] + bot + "add_phone_number_button",
                on_click=add_phone_number,
                # args=(bot),
                kwargs={"key": bot},
            )
            column_one, column_two = st.columns((1, 1))
            with column_one:
                st.button(
                    label="Update",
                    key=bot + "submit",
                    type="primary",
                    on_click=update_data,
                    args=(bot,),
                )
            with column_two:
                st.button(
                    label="Remove Knowledge Base",
                    key=bot + "remove",
                    type="primary",
                    on_click=remove_bot,
                    args=(bot,),
                )


if __name__ == "__main__":
    main()
