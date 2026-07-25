import streamlit as st


def hero(title, subtitle):
    st.markdown(f"""
    <div class="hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_title(title):
    st.markdown(f"""
    <div class="section-title">{title}</div>
    """, unsafe_allow_html=True)