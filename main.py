import streamlit as st
import pandas as pd
from model import *

# st.title('This is the title.')
st.markdown("<h1 style='text-align: center;'>Search the Best Course<br>for You</h1>", unsafe_allow_html=True)

query = st.text_input('')
documents = get_documents_dict()

if query:
    results = get_top_5_related(query)
    for i in results:
        st.markdown(f'<h3>{documents[i]}</h3>', unsafe_allow_html=True)
        st.markdown(get_course_link(course_num=i), unsafe_allow_html=True)
