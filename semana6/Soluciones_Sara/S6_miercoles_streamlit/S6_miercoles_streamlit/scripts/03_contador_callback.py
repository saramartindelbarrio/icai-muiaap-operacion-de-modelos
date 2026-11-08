import streamlit as st
st.title("Contador con callback")
if "count" not in st.session_state:
    st.session_state.count = 0
def increment():
    st.session_state.count += 1
st.button("Sumar", on_click=increment)#Aqui le pasas la función a Streamlit para que la ejecute cuando pulses el botón
#Si se hiciese st.button("Sumar", on_click=increment()) estás ejecutando la función inmediatamente, mientras Python construye la interfaz, en lugar de esperar el clic
st.metric("Cuenta", st.session_state.count)
