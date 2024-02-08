from datetime import datetime, timedelta

import extra_streamlit_components as stx
import httpx
import jwt
import streamlit as st

state = st.session_state
st.set_page_config(layout="centered")
cookie_manager = stx.CookieManager()


def init_state():
    if "email" not in state:
        state["email"] = None
    if "password" not in state:
        state["password"] = None
    if "authentication_status" not in state:
        state["authentication_status"] = None
    if "logout" not in state:
        state["logout"] = None
    if "uuid_number" not in state:
        state["uuid_number"] = ""
    if "name" not in state:
        state["name"] = ""
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


def _token_encode(expiry_date, email) -> str:
    return jwt.encode(
        {"email": email, "exp_date": expiry_date},
        "some_signature_key",
        algorithm="HS256",
    )


def _token_decode(token) -> str:
    try:
        return jwt.decode(token, "some_signature_key", algorithms=["HS256"])
    except Exception:
        return False


def _check_cookie():
    token = cookie_manager.get("Some cookie name")
    if token is not None:
        token = _token_decode(token)
        if token is not False:
            print("INSIDE TOKEN")
            print(token)
            if not state["logout"]:
                if token["exp_date"] > datetime.utcnow().timestamp():
                    if "email" in token:
                        state["email"] = token["email"]
                        state["authentication_status"] = True
                        print(state)


def _set_state_cb(**kwargs):
    for state_key, widget_key in kwargs.items():
        val = state.get(widget_key, None)
        if val is not None or val == "":
            setattr(state, state_key, state[widget_key])


def _set_login_cb(email, password):
    if login(email, password):
        expiry_date_time = datetime.now() + timedelta(days=30.0)
        expiry_date = expiry_date_time.timestamp()
        token = _token_encode(expiry_date, email)
        cookie_manager.set(
            "Some cookie name",
            token,
            expires_at=expiry_date_time,
        )
        state["authentication_status"] = True
        state["logout"] = False


# Function to check login credentials
def login(email, password):
    print("INSIDE LOGIN")
    print("EMAIL", email)
    print("PASSWORD", password)
    return (email == "a@gmail.com" and password == "b") or (
        email == "a" and password == "b"
    )


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
    pass


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
                    value=state.email,
                    key="reg_email_input",
                    on_change=_set_state_cb,
                    kwargs={"email": "reg_email_input"},
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
                            state.email,
                            state.reg_password,
                            state.confirm_password,
                        ),
                    )

    if state["authentication_status"] is True:
        st.title("Upload your files")
        uploaded_files = st.file_uploader(
            label="Files Upload", accept_multiple_files=True
        )
        url = "http://127.0.0.1:8000/upload-files"
        files = []
        for uploaded_file in uploaded_files:
            files.append(("files", uploaded_file))
        if len(files) > 0:
            response = httpx.post(url=url, files=files, timeout=60)
            response = response.json()
            state["uuid_number"] = response["uuid_number"]
            st.header(f"Your UUID number is {state['uuid_number']}")
        print("Login successful from the other side")
        _, column_two, _ = st.columns(3)
        with column_two:
            st.button(label="Logout", on_click=logout)


if __name__ == "__main__":
    main()
