import streamlit as st
from logics.accounts import login

st.set_page_config(layout= 'centered')

def main():

    st.markdown("""
    <style>
        [data-testid=stSidebar] {
            background-color: #3e3e40;
        }
    </style>
    """, unsafe_allow_html=True)
    with st.sidebar:
            st.image("./Animations/stock.png", 
                    #caption="Your PNG caption",
                    width=350)                

    #st.sidebar.title("hAin")           
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)


    st.sidebar.page_link("main.py",           label="Login",    icon="🔐")
    st.sidebar.page_link("pages/register.py", label="Register", icon="👤")
    st.sidebar.page_link("pages/forgot.py",   label="Forgot Credential",   icon="❓")

    login()

if __name__ == "__main__":
    main()
