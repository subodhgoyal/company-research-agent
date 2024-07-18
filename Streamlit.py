import streamlit as st
from langchain_community.llms import Ollama

llm = Ollama(model="qwen2:0.5b")

st.title("Fun bffot")

prompt = st.text_area("Typesttr here:")

if st.button("Chat"):
    if prompt:
        with st.spinner("Generating Response..."):
            st.write(llm.stream(prompt, stop=['<|eot_id|>']))