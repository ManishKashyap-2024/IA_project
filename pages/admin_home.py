import streamlit as st
from logics.database import create_connection, get_user_info
from streamlit_extras.switch_page_button import switch_page


st.set_page_config(layout="wide")



st.sidebar.page_link("pages/admin_home.py", label="Home",  icon="🏠")
st.sidebar.page_link("pages/admin.py",      label="Admin", icon="👤")


st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #3e3e40;
    }
</style>
""", unsafe_allow_html=True)
with st.sidebar:
        st.image("./Animations/stock2.jpg", 
                #caption="Your PNG caption",
                width=350)  






from logics.stock_prices import StockAnalysisApp

app = StockAnalysisApp()

app.init_state_variables()
app.stock_analysis()


logout = st.sidebar.button("LogOut")
if logout:
    switch_page("Main")



