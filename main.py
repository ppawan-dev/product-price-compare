from streamlit.web import bootstrap

if __name__ == "__main__":
    bootstrap.run(
        "streamlit_app.py",
        command_line="streamlit run streamlit_app.py",
        args=[],
        flag_options={}
    )
