import streamlit as st
import os
import tempfile
from PIL import Image
from test import main as main_process

st.set_page_config(
    page_title="IR Spectrum Curve Extractor",
    layout="wide",  
)

st.title("🖼️ IR Spectrum Curve Extractor")

with st.container():
    st.write("### ⚙️ Parameter Settings")
    col_input1, col_input2, col_input3 = st.columns([1, 1, 2]) # 比例设为1:1:2，让输入框紧凑点
    with col_input1:
        y_min_raw = st.text_input("Please enter Y-axis lower limit", value="0")
    with col_input2:
        y_max_raw = st.text_input("Please enter Y-axis upper limit", value="100")
    
    try:
        y_min = float(y_min_raw)
        y_max = float(y_max_raw)
    except ValueError:
        st.warning("Please enter valid numbers")
        y_min, y_max = 0.0, 100.0

uploaded_file = st.file_uploader("upload picture", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    if st.button("Run", type="primary", use_container_width=True):
        with st.spinner("processing..."):
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name 
            
            try:
                processed_path = main_process(temp_file_path, y_axis_range=(y_min, y_max))
                
                st.markdown("---") 
                
                st.subheader("🔍 1. Raw Image")
                original_image = Image.open(uploaded_file)
                st.image(original_image, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True) 
                
                st.subheader("✨ 2.Processed Image")
                if os.path.exists(processed_path):
                    processed_image = Image.open(processed_path)
                    st.image(processed_image, use_container_width=True)
                    
                    st.success("success!")
                    with open(processed_path, "rb") as f:
                        st.download_button("💾 download result", f, "result.png", "image/png")
                else:
                    st.error("error")
                        
            except Exception as e:
                st.error(f"error: {e}")

st.markdown("""
    <style>
    .main > div {
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
    }
    img {
        border: 1px solid #ddd;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)