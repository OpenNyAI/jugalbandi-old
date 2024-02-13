import time
import uuid
from datetime import datetime, timedelta

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
from streamlit_modal import Modal
from tenant_repository import TenantRepository
import re

# from PIL import Image


def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(./media/jb_logo.png);
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 20px 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# def add_logo(logo_path, width, height):
#     """Read and return a resized logo"""
#     logo = Image.open(logo_path)
#     modified_logo = logo.resize((width, height))
#     return modified_logo


state = st.session_state
st.set_page_config(page_title="Jugalbandi", page_icon="😎", layout="centered")
# add_logo()
cookie_manager = stx.CookieManager()
validator = InputValidator()
tenant_repository = TenantRepository()


modal = Modal(
    "Demo Modal",
    key="demo-modal",
    # Optional
    padding=20,  # default value
    max_width=744,  # default value
)


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
    if "phone_numbers" not in state:
        state["phone_numbers"] = {}
    if "rows" not in state:
        state["rows"] = ["base_id"]


def _check_cookie():
    token = cookie_manager.get("Some cookie name")
    if token is not None:
        token = token_decode(token)
        if token is not False:
            print("INSIDE TOKEN")
            print(token)
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
    print("INSIDE LOGIN")
    try:
        if not validator.validate_input_for_length(email):
            raise Exception("Email should not be empty")
        if not validator.validate_input_for_length(password):
            raise Exception("Password should not be empty")
        tenant_detail = tenant_repository.get_tenant_details(email)
        if tenant_detail is None:
            raise Exception("Invalid login credentials")
        else:
            return verify_password(password, tenant_detail[-1])
    except Exception as e:
        st.error(e, icon="🚨")


def logout():
    print("INSIDE LOGOUT")
    cookie_manager.delete("Some cookie name")
    print("BEFORE", cookie_manager.get(cookie="Some cookie name"))
    if "Some cookie name" in cookie_manager.cookies:
        del cookie_manager.cookies["Some cookie name"]
    print("AFTER", cookie_manager.get(cookie="Some cookie name"))
    state["logout"] = True
    state["email"] = None
    state["password"] = None
    state["authentication_status"] = None


# Inject custom CSS to move the logout button to the top-right corner
st.markdown(
    """
    <style>
    #logout-button-container {
        position: absolute;
        top: 10px;
        right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Add a container for the logout button and apply custom CSS
st.markdown('<div id="logout-button-container">', unsafe_allow_html=True)

# Add the logout button
st.button(label="Logout", on_click=logout, type="primary")

# Close the container
st.markdown("</div>", unsafe_allow_html=True)


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


def _set_signup_cb(name, email, reg_password, confirm_password):
    try:
        if not validator.validate_input_for_length(name):
            raise Exception("Name should not be empty")
        if not validator.validate_input_for_length(email):
            raise Exception("Email should not be empty")
        if not validator.validate_email(email):
            raise Exception("Email is not valid")
        registered_emails = tenant_repository.get_all_tenant_emails()
        if email in registered_emails:
            raise Exception("Email is already registered")
        if not validator.validate_input_for_length(
            reg_password
        ) or not validator.validate_input_for_length(confirm_password):
            raise Exception("Password/confirm password fields cannot be empty")
        if reg_password != confirm_password:
            raise Exception("Passwords do not match")
        print("Inside Signup")
        with st.spinner("Registration in progress...."):
            tenant_repository.insert_into_tenant(
                name=name,
                email_id=email,
                api_key=generate_api_key(),
                password=get_hashed_password(password=reg_password),
            )
        print("Insertion complete")
        st.toast("Registration successful", icon="✅")
        time.sleep(1)
        is_login_option()
    except Exception as e:
        st.error(e, icon="🚨")


def validate_phone_number(phone_number):
    # Define a regular expression for a simple phone number pattern
    pattern = re.compile(
        r"^\d{10}$"
    )  # Assuming a 10-digit phone number without any special characters

    # Check if the entered phone number matches the pattern
    if pattern.match(phone_number):
        return True
    else:
        return False


def _remove_phone_number(key):
    print("state", state["phone_numbers"])
    del state["phone_numbers"][key]
    print("state", state["phone_numbers"])


def create_input_components(key):
    row_container = st.empty()
    row_columns = row_container.columns((2, 2))
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
        st.button(
            label="Remove",
            key="rm_phone_number_input" + str(key),
            on_click=_remove_phone_number,
            args=(key,),
            type="primary",
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
                "Document name should not contain emojis and should be between 1 & 15 characters"
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
                    state["uuid_number"],
                    state["document_name"].strip(),
                    file_names,
                    state["prompt"],
                )
                tenant_details = tenant_repository.get_tenant_details(state["email"])
                for _, value in state["phone_numbers"].items():
                    tenant_repository.insert_into_tenant_bot(
                        tenant_details[2],
                        state["uuid_number"],
                        value.get("country_phone_code") + value.get("phone_number"),
                    )
                modal.open()
    except Exception as e:
        st.error(e, icon="🚨")


def main():
    init_state()
    st.title("Jugalbandi :sunglasses:")
    if not state["authentication_status"]:
        _check_cookie()
        if not state["authentication_status"]:
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
                            state.name,
                            state.reg_email,
                            state.reg_password,
                            state.confirm_password,
                        ),
                    )

    if state["authentication_status"] is True:
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

            st.markdown("---")
            st.title("User Assignment")

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

            # Add a container for the button and apply custom CSS
            # st.markdown('<div class="add-user">', unsafe_allow_html=True)

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
            if state["uuid_number"]:
                st.toast(
                    f"Your knowledge base {state['document_name']} has been uploaded!",
                    icon="✅",
                )

        if modal.is_open():
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
            st.button(label="Logout", on_click=logout, type="primary")
            tenant_details = tenant_repository.get_tenant_details(state["email"])
            st.title(f"Hello {tenant_details[0]}")


if __name__ == "__main__":
    main()
