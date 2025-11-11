# ======================================================
# 🌐 Streamlit FTP Browser – All-in-One, Ready to Deploy
# ======================================================

import streamlit as st
from ftplib import FTP, error_perm
import io
import pandas as pd
from PIL import Image
import os
import tempfile
import base64

# Page configuration
st.set_page_config(
    page_title="FTP Cloud Browser", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'ftp' not in st.session_state:
    st.session_state.ftp = None
if 'current_dir' not in st.session_state:
    st.session_state.current_dir = "/"
if 'connection_error' not in st.session_state:
    st.session_state.connection_error = None

# Custom CSS for better UI
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .file-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .file-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .connection-status {
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: bold;
    }
    .connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .ftp-link {
        background: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        font-family: monospace;
        border: 2px solid #4CAF50;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🌐 FTP Cloud Storage Browser")
st.markdown("**Read-Only FTP Access with File Preview & Direct Links**")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("🔧 FTP Configuration")
    
    # Connection mode selection
    connection_mode = st.radio("Connection Mode", ["Anonymous FTP", "Authenticated FTP"], index=0)
    
    if connection_mode == "Anonymous FTP":
        st.info("Using anonymous FTP connection")
        # Pre-configured anonymous FTP servers for testing
        ftp_servers = {
            "Tele2 Speedtest (Sweden)": {"host": "speedtest.tele2.net", "user": "anonymous", "pass": "anonymous@"},
            "UNC Anonymous FTP": {"host": "ftp.unc.edu", "user": "anonymous", "pass": "anonymous@"},
            "Custom Anonymous Server": {"host": "", "user": "anonymous", "pass": "anonymous@"}
        }
        
        selected_server = st.selectbox("Select FTP Server", list(ftp_servers.keys()))
        if selected_server == "Custom Anonymous Server":
            FTP_HOST = st.text_input("FTP Host", placeholder="ftp.example.com")
        else:
            FTP_HOST = ftp_servers[selected_server]["host"]
            st.info(f"Connecting to: {FTP_HOST}")
        
        FTP_USER = ftp_servers[selected_server]["user"]
        FTP_PASS = ftp_servers[selected_server]["pass"]
        
    else:  # Authenticated FTP
        st.warning("⚠️ Ensure your FTP server allows external connections")
        FTP_HOST = st.text_input("FTP Host", placeholder="ftp.yourserver.com")
        FTP_USER = st.text_input("FTP Username", placeholder="your_username")
        FTP_PASS = st.text_input("FTP Password", type="password", placeholder="your_password")
    
    # Connection button
    if st.button("🚀 Connect to FTP", type="primary", use_container_width=True):
        with st.spinner("Connecting to FTP server..."):
            try:
                # Test connection
                ftp = FTP(FTP_HOST, timeout=20)
                ftp.login(FTP_USER, FTP_PASS)
                ftp.quit()
                
                st.session_state.connected = True
                st.session_state.ftp_config = {
                    "host": FTP_HOST,
                    "user": FTP_USER,
                    "pass": FTP_PASS
                }
                st.session_state.connection_error = None
                st.success("✅ Connected successfully!")
                st.balloons()
                
            except Exception as e:
                st.session_state.connected = False
                st.session_state.connection_error = str(e)
                st.error(f"❌ Connection failed: {e}")
    
    # Display connection status
    if st.session_state.connected:
        st.markdown('<div class="connection-status connected">🟢 Connected</div>', unsafe_allow_html=True)
        st.info(f"Host: {st.session_state.ftp_config['host']}")
    else:
        st.markdown('<div class="connection-status disconnected">🔴 Disconnected</div>', unsafe_allow_html=True)
        if st.session_state.connection_error:
            st.error(f"Last error: {st.session_state.connection_error}")

    st.markdown("---")
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. **Choose Connection Mode**
       - Anonymous: Use public FTP servers
       - Authenticated: Use your private FTP
    
    2. **Enter FTP Details**
       - Host: FTP server address
       - Credentials: Username & password
    
    3. **Connect & Browse**
       - Click 'Connect to FTP'
       - Browse files and folders
       - Preview files directly
    
    4. **Get Direct Links**
       - Copy FTP URLs for external access
       - Use in any FTP client
    """)

# Main content area
if st.session_state.connected:
    try:
        # FTP connection functions
        def get_ftp_connection():
            config = st.session_state.ftp_config
            ftp = FTP(config["host"], timeout=30)
            ftp.login(config["user"], config["pass"])
            return ftp
        
        def list_files(directory="."):
            try:
                ftp = get_ftp_connection()
                ftp.cwd(directory)
                files = []
                ftp.retrlines('LIST', files.append)
                ftp.quit()
                
                # Parse file listings
                file_list = []
                for file_info in files:
                    parts = file_info.split()
                    if len(parts) >= 9:
                        is_dir = parts[0].startswith('d')
                        name = ' '.join(parts[8:])
                        size = parts[4] if not is_dir else 'DIR'
                        file_list.append({
                            'name': name,
                            'is_dir': is_dir,
                            'size': size,
                            'raw_info': file_info
                        })
                return file_list
            except Exception as e:
                st.error(f"❌ Failed to list files: {e}")
                return []
        
        def read_file(remote_path):
            try:
                ftp = get_ftp_connection()
                file_buffer = io.BytesIO()
                ftp.retrbinary(f"RETR {remote_path}", file_buffer.write)
                ftp.quit()
                file_buffer.seek(0)
                return file_buffer
            except Exception as e:
                st.error(f"❌ Failed to read file: {e}")
                return None
        
        def generate_ftp_link(remote_path):
            config = st.session_state.ftp_config
            # Create FTP URL
            if config["user"] == "anonymous":
                return f"ftp://{config['host']}/{remote_path}"
            else:
                return f"ftp://{config['user']}:{config['pass']}@{config['host']}/{remote_path}"
        
        # Current directory navigation
        col1, col2 = st.columns([3, 1])
        with col1:
            current_dir = st.text_input("📂 Current Directory", value=st.session_state.current_dir)
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Navigate to parent directory
        if st.button("⬆️ Parent Directory") and current_dir != "/":
            parent_dir = "/".join(current_dir.rstrip("/").split("/")[:-1])
            if not parent_dir:
                parent_dir = "/"
            st.session_state.current_dir = parent_dir
            st.rerun()
        
        # List files in current directory
        with st.spinner("Loading files..."):
            files = list_files(current_dir)
        
        if files:
            st.success(f"✅ Found {len(files)} item(s) in {current_dir}")
            
            # File browser
            for file_info in files:
                with st.container():
                    st.markdown('<div class="file-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                    
                    with col1:
                        if file_info['is_dir']:
                            st.markdown(f"📁 **{file_info['name']}**")
                        else:
                            st.markdown(f"📄 {file_info['name']}")
                    
                    with col2:
                        st.markdown(f"*{file_info['size']}*")
                    
                    with col3:
                        if file_info['is_dir']:
                            if st.button("📂 Open", key=f"open_{file_info['name']}"):
                                new_dir = f"{current_dir.rstrip('/')}/{file_info['name']}"
                                st.session_state.current_dir = new_dir
                                st.rerun()
                        else:
                            st.markdown("File")
                    
                    with col4:
                        if not file_info['is_dir']:
                            remote_path = f"{current_dir.rstrip('/')}/{file_info['name']}"
                            ftp_link = generate_ftp_link(remote_path)
                            
                            # Copy button for FTP link
                            if st.button("📋 Copy Link", key=f"copy_{file_info['name']}"):
                                st.code(ftp_link, language="text")
                                st.info("🔗 FTP link generated above!")
                            
                            # Preview button for supported file types
                            if st.button("👁️ Preview", key=f"preview_{file_info['name']}"):
                                with st.spinner("Loading file..."):
                                    file_buffer = read_file(remote_path)
                                    if file_buffer:
                                        file_name = file_info['name'].lower()
                                        
                                        # CSV files
                                        if file_name.endswith('.csv'):
                                            try:
                                                df = pd.read_csv(file_buffer)
                                                st.dataframe(df, use_container_width=True)
                                                st.info(f"📊 CSV file with {len(df)} rows and {len(df.columns)} columns")
                                            except Exception as e:
                                                st.error(f"Failed to read CSV: {e}")
                                        
                                        # Image files
                                        elif file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                                            try:
                                                img = Image.open(file_buffer)
                                                st.image(img, caption=file_info['name'], use_container_width=True)
                                            except Exception as e:
                                                st.error(f"Failed to load image: {e}")
                                        
                                        # Text files
                                        elif file_name.endswith(('.txt', '.md', '.py', '.json', '.xml', '.html', '.css', '.js')):
                                            try:
                                                text_content = file_buffer.getvalue().decode('utf-8', errors='ignore')
                                                st.text_area("File Content", text_content, height=400)
                                                
                                                # Download button for text files
                                                st.download_button(
                                                    label="📥 Download File",
                                                    data=text_content,
                                                    file_name=file_info['name'],
                                                    mime="text/plain"
                                                )
                                            except Exception as e:
                                                st.error(f"Failed to read text file: {e}")
                                        
                                        # Other files - offer download
                                        else:
                                            st.info("📁 Binary file - use the FTP link above to download")
                                            
                                            # Try to offer download anyway
                                            try:
                                                file_data = file_buffer.getvalue()
                                                st.download_button(
                                                    label="📥 Download File",
                                                    data=file_data,
                                                    file_name=file_info['name']
                                                )
                                            except:
                                                pass
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.warning("📭 No files found in this directory or connection failed")
            if current_dir != "/":
                st.info("💡 Try navigating to the root directory")
    
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        st.info("🔄 Please check your FTP connection settings and try again")

else:
    # Not connected state
    st.info("🔌 Please configure and connect to an FTP server using the sidebar")
    
    # Demo section
    with st.expander("🎯 Quick Demo - Try Anonymous FTP"):
        st.markdown("""
        ### Ready-to-use Anonymous FTP Servers:
        
        1. **Tele2 Speedtest (Sweden)**
           - Host: `speedtest.tele2.net`
           - User: `anonymous`
           - Password: `anonymous@`
           - Contains: Speed test files
        
        2. **UNC Anonymous FTP**
           - Host: `ftp.unc.edu`
           - User: `anonymous`
           - Password: `anonymous@`
           - Contains: Public software archives
        
        3. **Your Custom Server**
           - Any FTP server that allows anonymous access
        
        ### How to Use:
        1. Select 'Anonymous FTP' in the sidebar
        2. Choose a server from the dropdown
        3. Click 'Connect to FTP'
        4. Start browsing files!
        """)
    
    # Features showcase
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 🌐 **Multi-Mode**
        - Anonymous FTP access
        - Authenticated connections
        - Custom server support
        - Connection testing
        """)
    
    with col2:
        st.markdown("""
        ### 📁 **File Operations**
        - Browse directories
        - File previews
        - Direct FTP links
        - Download capabilities
        """)
    
    with col3:
        st.markdown("""
        ### 🚀 **Easy Deploy**
        - Single file app
        - Streamlit Cloud ready
        - Auto-configuration
        - No setup required
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.8);'>
    <p><strong>💡 Pro Tip:</strong> Upload this single App.py file to GitHub and deploy on Streamlit Cloud for instant FTP browsing!</p>
    <p>Built with ❤️ using Streamlit | FTP Cloud Browser v2.0</p>
</div>
""", unsafe_allow_html=True)
