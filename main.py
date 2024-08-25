import streamlit as st

from logics.accounts import login


st.set_page_config(layout= 'centered')


def main():



    st.sidebar.page_link("main.py",           label="Login",    icon="🔐")
    st.sidebar.page_link("pages/register.py", label="Register", icon="👤")
    st.sidebar.page_link("pages/forgot.py",   label="Forgot Creditional",   icon="❓")

    login()

if __name__ == "__main__":
    main()
