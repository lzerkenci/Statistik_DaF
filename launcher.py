import os
import streamlit.web.bootstrap

script_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(script_dir, "app.py")

streamlit.web.bootstrap.run(app_path, "", [], {})