import json
import re
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import extra_streamlit_components as stx
import httpx
import streamlit as st
from helper import (
    InputValidator,
    country_phone_code_mapping,
    generate_api_key,
    get_hashed_password,
    token_decode,
    token_encode,
    verify_password,
)
from streamlit.source_util import _on_pages_changed, get_pages
from streamlit_modal import Modal
from tenant_repository import TenantRepository

state = st.session_state
st.set_page_config(
    page_title="Jugalbandi",
    page_icon="😎",
    layout="centered",
)
st.image("./media/jb_logo.png")
cookie_manager = stx.CookieManager()
validator = InputValidator()
tenant_repository = TenantRepository()
DEFAULT_PAGE = "Create_Knowledge_Base.py"


modal = Modal(
    title="📱 Whatsapp Assistant QR Code",
    key="wapp-modal",
    padding=20,
    max_width=744,
)


def get_all_pages():
    default_pages = get_pages(DEFAULT_PAGE)
    pages_path = Path("pages.json")
    if pages_path.exists():
        saved_default_pages = json.loads(pages_path.read_text())
    else:
        saved_default_pages = default_pages.copy()
        pages_path.write_text(json.dumps(default_pages, indent=4))

    return saved_default_pages


def clear_all_but_first_page():
    current_pages = get_pages(DEFAULT_PAGE)
    if len(current_pages.keys()) == 1:
        return

    get_all_pages()
    # Remove all but the first page
    key, val = list(current_pages.items())[0]
    current_pages.clear()
    current_pages[key] = val

    _on_pages_changed.send()


def show_all_pages():
    current_pages = get_pages(DEFAULT_PAGE)
    saved_pages = get_all_pages()
    # Replace all the missing pages
    for key in saved_pages:
        if key not in current_pages:
            current_pages[key] = saved_pages[key]

    _on_pages_changed.send()


def init_state():
    if "email" not in state:
        state["email"] = ""
    if "password" not in state:
        state["password"] = ""
    if "authentication_status" not in state:
        state["authentication_status"] = None
    if "logout" not in state:
        state["logout"] = None
    if "uuid_number" not in state:
        state["uuid_number"] = ""
    if "name" not in state:
        state["name"] = ""
    if "reg_email" not in state:
        state["reg_email"] = ""
    if "reg_phone_number" not in state:
        state["reg_phone_number"] = ""
    if "reg_password" not in state:
        state["reg_password"] = ""
    if "confirm_password" not in state:
        state["confirm_password"] = ""
    if "login_button_option" not in state:
        state["login_button_option"] = True
    if "login_button_type" not in state:
        state["login_button_type"] = "primary"
    if "signup_button_option" not in state:
        state["signup_button_option"] = False
    if "signup_button_type" not in state:
        state["signup_button_type"] = "secondary"
    if "document_name" not in state:
        state["document_name"] = ""
    if "prompt" not in state:
        state["prompt"] = (
            "You are a helpful assistant who helps with answering questions based on the provided information. If the information cannot be found in the text provided, you admit that I don't know"
        )
    if "welcome_message" not in state:
        state["welcome_message"] = ""
    if "phone_numbers" not in state:
        state["phone_numbers"] = {}
    if "rows" not in state:
        state["rows"] = ["base_id"]


def _check_cookie():
    token = cookie_manager.get("Some cookie name")
    if token is not None:
        token = token_decode(token)
        if token is not False:
            if not state["logout"]:
                if token["exp_date"] > datetime.utcnow().timestamp():
                    if "email" in token:
                        state["email"] = token["email"]
                        state["authentication_status"] = True


def _set_state_cb(**kwargs):
    for state_key, widget_key in kwargs.items():
        val = state.get(widget_key, None)
        if val is not None or val == "":
            setattr(state, state_key, state[widget_key])


def _set_login_cb(email, password):
    if login(email, password):
        expiry_date_time = datetime.now() + timedelta(days=30.0)
        expiry_date = expiry_date_time.timestamp()
        token = token_encode(expiry_date, email)
        cookie_manager.set(
            "Some cookie name",
            token,
            expires_at=expiry_date_time,
        )
        state["authentication_status"] = True
        state["logout"] = False


def login(email, password):
    try:
        if not validator.validate_input_for_length(email):
            raise Exception("Email should not be empty")
        if not validator.validate_input_for_length(password):
            raise Exception("Password should not be empty")
        tenant_detail = tenant_repository.get_tenant_details(email)
        if tenant_detail is None:
            raise Exception("Invalid login credentials")
        else:
            return verify_password(password, tenant_detail[5])
    except Exception as e:
        st.error(e, icon="🚨")


def logout():
    cookie_manager.delete("Some cookie name")
    if "Some cookie name" in cookie_manager.cookies:
        del cookie_manager.cookies["Some cookie name"]
    state["logout"] = True
    state["email"] = None
    state["password"] = None
    state["authentication_status"] = None


def is_login_option():
    state["login_button_option"] = True
    state["signup_button_option"] = False
    state["login_button_type"] = "primary"
    state["signup_button_type"] = "secondary"


def is_signup_option():
    state["signup_button_option"] = True
    state["login_button_option"] = False
    state["signup_button_type"] = "primary"
    state["login_button_type"] = "secondary"


def _set_signup_cb(name, email, phone_number, reg_password, confirm_password):
    try:
        if not validator.validate_input_for_length(name):
            raise Exception("Name should not be empty")
        if not validator.validate_input_for_length(email):
            raise Exception("Email should not be empty")
        if not validator.validate_email(email):
            raise Exception("Email is not valid")
        if not validator.validate_input_for_length(phone_number):
            raise Exception("Phone number should not be empty")
        registered_emails = tenant_repository.get_all_tenant_emails()
        if email in registered_emails:
            raise Exception("Email is already registered")
        if not validator.validate_input_for_length(
            reg_password
        ) or not validator.validate_input_for_length(confirm_password):
            raise Exception("Password/confirm password fields cannot be empty")
        if reg_password != confirm_password:
            raise Exception("Passwords do not match")
        with st.spinner("Registration in progress...."):
            tenant_repository.insert_into_tenant(
                name=name,
                email_id=email,
                phone_number=phone_number,
                api_key=generate_api_key(),
                password=get_hashed_password(password=reg_password),
            )
        st.toast("Registration successful", icon="✅")
        time.sleep(1)
        is_login_option()
    except Exception as e:
        st.error(e, icon="🚨")


def validate_phone_number(phone_number):
    pattern = re.compile(r"^\d{10}$")
    return pattern.match(phone_number)


def _remove_phone_number(key):
    del state["phone_numbers"][key]
    state["rows"].remove(key)


def create_input_components(key):
    row_container = st.empty()
    row_columns = row_container.columns((3, 2, 1))
    with row_columns[0]:
        default_value = "India"
        country_list = list(country_phone_code_mapping.keys())
        selected_country = st.selectbox(
            label="Select the country",
            key="country_select_box" + str(key),
            options=tuple(country_phone_code_mapping.keys()),
            index=country_list.index(default_value),
        )
    with row_columns[1]:
        phone_number = st.text_input(
            "Enter the phone number",
            key="phone_number_input" + str(key),
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
            key="rm_phone_number_input" + str(key),
            on_click=_remove_phone_number,
            args=(key,),
            type="secondary",
        )
        if phone_number and not validate_phone_number(phone_number):
            st.error(
                "Invalid phone number. Please enter a valid number without spaces or special characters."
            )
    state["phone_numbers"][key] = {
        "country_phone_code": country_phone_code_mapping[selected_country],
        "phone_number": phone_number,
    }


def add_phone_numbers():
    element_id = uuid.uuid4()
    state["rows"].append(str(element_id))


def _submit_data_cb(files):
    url = "https://api.jugalbandi.ai/upload-files"
    try:
        if len(files) < 1:
            raise Exception("Files should not be empty")
        elif not validator.validate_document_set_name(
            document_set_name=state["document_name"]
        ):
            raise Exception(
                "Knowledge base name should not contain emojis and should be between 1 & 15 characters"
            )
        else:
            for _, value in state["phone_numbers"].items():
                if value.get("phone_number") == "":
                    raise Exception("Phone number should not be empty")
            with st.spinner("Uploading in progress"):
                response = httpx.post(url=url, files=files, timeout=60)
                response = response.json()
                state["uuid_number"] = response["uuid_number"]
                file_names = [file[1].name for file in files]
                tenant_repository.insert_into_tenant_document(
                    document_uuid=state["uuid_number"],
                    document_name=state["document_name"].strip(),
                    documents_list=file_names,
                    prompt=state["prompt"],
                    welcome_message=state["welcome_message"],
                )
                tenant_details = tenant_repository.get_tenant_details(state["email"])
                tenant_repository.insert_into_tenant_bot(
                    tenant_api_key=tenant_details[2],
                    document_uuid=state["uuid_number"],
                    phone_number="91" + tenant_details[6],
                    country_code="91",
                )
                for _, value in state["phone_numbers"].items():
                    tenant_repository.insert_into_tenant_bot(
                        tenant_api_key=tenant_details[2],
                        document_uuid=state["uuid_number"],
                        phone_number=value.get("country_phone_code")
                        + value.get("phone_number"),
                        country_code=value.get("country_phone_code"),
                    )
        modal.open()
    except Exception as e:
        st.error(e, icon="🚨")


def main():
    init_state()
    if not state["authentication_status"]:
        _check_cookie()
        if not state["authentication_status"]:
            clear_all_but_first_page()
            st.subheader("Choose an action")
            login_column, signup_column = st.columns(2)
            login_column.button(
                label="Login", on_click=is_login_option, type=state["login_button_type"]
            )
            if state["login_button_option"]:
                st.text_input(
                    "Email:",
                    value=state.email,
                    key="email_input",
                    on_change=_set_state_cb,
                    kwargs={"email": "email_input"},
                )
                st.text_input(
                    "Password:",
                    type="password",
                    value=state.password,
                    key="password_input",
                    on_change=_set_state_cb,
                    kwargs={"password": "password_input"},
                )
                _, column_two, _ = st.columns(3)
                with column_two:
                    st.button(
                        label="Submit",
                        key="login_submit",
                        on_click=_set_login_cb,
                        args=(state.email, state.password),
                    )

            signup_column.button(
                label="Sign up",
                on_click=is_signup_option,
                type=state["signup_button_type"],
            )
            if state["signup_button_option"]:
                st.text_input(
                    "Name:",
                    value=state.name,
                    key="name_input",
                    on_change=_set_state_cb,
                    kwargs={"name": "name_input"},
                )
                st.text_input(
                    "Email:",
                    value=state.reg_email,
                    key="reg_email_input",
                    on_change=_set_state_cb,
                    kwargs={"reg_email": "reg_email_input"},
                )
                st.text_input(
                    "Phone number:",
                    value=state.reg_phone_number,
                    key="reg_phone_number_input",
                    on_change=_set_state_cb,
                    kwargs={"reg_phone_number": "reg_phone_number_input"},
                )
                st.text_input(
                    "Password:",
                    type="password",
                    value=state.reg_password,
                    key="reg_password_input",
                    on_change=_set_state_cb,
                    kwargs={"reg_password": "reg_password_input"},
                )
                st.text_input(
                    "Confirm password:",
                    type="password",
                    value=state.confirm_password,
                    key="confirm_password_input",
                    on_change=_set_state_cb,
                    kwargs={"confirm_password": "confirm_password_input"},
                )
                _, column_two, _ = st.columns(3)
                with column_two:
                    st.button(
                        label="Submit",
                        key="signup_submit",
                        on_click=_set_signup_cb,
                        args=(
                            state["name"],
                            state["reg_email"],
                            state["reg_phone_number"],
                            state["reg_password"],
                            state["confirm_password"],
                        ),
                    )

    if state["authentication_status"] is True:
        show_all_pages()
        with st.container():
            st.title("Upload Data")
            uploaded_files = st.file_uploader(
                label="Files Upload", accept_multiple_files=True
            )
            files = []
            for uploaded_file in uploaded_files:
                files.append(("files", uploaded_file))
            st.text_input(
                "Knowledge Base Name:",
                value=state.document_name,
                key="document_name_input",
                on_change=_set_state_cb,
                kwargs={"document_name": "document_name_input"},
            )
            st.text_area(
                "Custom Prompt:",
                value=state.prompt,
                key="prompt_input",
                on_change=_set_state_cb,
                kwargs={"prompt": "prompt_input"},
            )
            st.text_area(
                "Welcome message:",
                value=state.welcome_message,
                key="welcome_message_input",
                on_change=_set_state_cb,
                kwargs={"welcome_message": "welcome_message_input"},
            )
            st.markdown("---")
            st.title("Phone number Assignment")

            # Inject custom CSS to move the button to the left
            st.markdown(
                """
                <style>
                .add_phone_number_button {
                    text-align: left;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            for i, row in enumerate(state["rows"]):
                st.markdown(f"User {i+1}")
                create_input_components(row)
            _, column_two, _ = st.columns(3)
            with column_two:
                st.button(
                    label="Add User",
                    key="add_phone_number_button",
                    on_click=add_phone_numbers,
                )
                st.button(
                    label="Submit",
                    key="files_submit",
                    on_click=_submit_data_cb,
                    type="primary",
                    kwargs={"files": files},
                )

        if modal.is_open():
            st.toast(
                f"Your knowledge base {state['document_name']} has been uploaded!",
                icon="✅",
            )
            with modal.container():
                _, column_two, _ = st.columns(3)
                with column_two:
                    st.image(
                        "jb_wa_qr.jpeg",
                        width=250,
                        caption="Scan this QR code to talk to your document over Whatsapp",
                    )

        st.markdown("***")
        with st.sidebar:
            tenant_details = tenant_repository.get_tenant_details(state["email"])
            st.title(f"Hello {tenant_details[0]}")
            st.button(label="Logout", key="logout", on_click=logout, type="primary")


if __name__ == "__main__":
    main()
