# ======================================================
# 🌐 Streamlit FTP Browser – All-in-One, Ready to Deploy
# ======================================================

import streamlit as st
from ftplib import FTP
import io
import pandas as pd
from PIL import Image

# ---- EDIT THESE THREE VALUES ONCE ----
FTP_HOST = "peedtest.tele2.net"      # e.g. "123.45.67.89" or "ftp.myserver.com"
FTP_USER = "anonymous"           # e.g. "gorden"
FTP_PASS = "anonymous@"           # e.g. "myStrongPassword"
# --------------------------------------

st.set_page_config(page_title="FTP Cloud Browser", page_icon="🌐", layout="wide")
st.title("🌐 FTP Cloud Storage (Read-Only Access)")

# ---------- FTP FUNCTIONS ----------
def ftp_connect():
    ftp = FTP(FTP_HOST, timeout=20)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def ftp_list_files(directory="."):
    try:
        ftp = ftp_connect()
        ftp.cwd(directory)
        files = ftp.nlst()
        ftp.quit()
        return files
    except Exception as e:
        st.error(f"❌ FTP listing failed: {e}")
        return []

def ftp_read_file(remote_path):
    try:
        ftp = ftp_connect()
        file_buffer = io.BytesIO()
        ftp.retrbinary(f"RETR {remote_path}", file_buffer.write)
        ftp.quit()
        file_buffer.seek(0)
        return file_buffer
    except Exception as e:
        st.error(f"❌ FTP read failed: {e}")
        return None

def ftp_public_link(remote_path):
    return f"ftp://{FTP_USER}:{FTP_PASS}@{FTP_HOST}/{remote_path}"

# ---------- STREAMLIT UI ----------
base_dir = st.text_input("📂 Remote directory path", value="/")
if st.button("🔄 List Files"):
    files = ftp_list_files(base_dir)
    if not files:
        st.warning("No files found or connection failed.")
    else:
        st.success(f"✅ Found {len(files)} file(s) in {base_dir}")
        selected = st.selectbox("Select a file to open:", files)
        if selected:
            file_link = ftp_public_link(f"{base_dir.rstrip('/')}/{selected}")
            st.code(file_link, language="text")
            st.markdown(f"[📥 Open in external FTP client]({file_link})")

            # Preview content
            if selected.lower().endswith(".csv"):
                buf = ftp_read_file(f"{base_dir.rstrip('/')}/{selected}")
                if buf:
                    df = pd.read_csv(buf)
                    st.dataframe(df)
            elif selected.lower().endswith((".jpg", ".jpeg", ".png")):
                buf = ftp_read_file(f"{base_dir.rstrip('/')}/{selected}")
                if buf:
                    img = Image.open(buf)
                    st.image(img, caption=selected, use_container_width=True)
            else:
                buf = ftp_read_file(f"{base_dir.rstrip('/')}/{selected}")
                if buf:
                    text = buf.getvalue().decode("utf-8", errors="ignore")
                    st.text_area("File content preview:", text, height=300)

st.markdown("---")
st.caption("💡 Upload this single App.py to GitHub → Deploy on streamlit.io → Ready to browse your FTP files.")

