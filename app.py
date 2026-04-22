import streamlit as st
import os
import tempfile
import pandas as pd  
from PIL import Image
from test import main as main_process

st.set_page_config(
    page_title="IR Spectrum Curve Extractor",
    layout="wide",  
)

st.title("🖼️ IR Spectrum Curve Extractor")

with st.container():
    st.write("### ⚙️ Parameter Settings")
    col_input1, col_input2, col_input3 = st.columns([1, 1, 2]) 
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
                processed_path, df = main_process(temp_file_path, y_axis_range=(y_min, y_max))
                
                st.markdown("---") 
                
                st.subheader("🔍 1. Raw Image")
                original_image = Image.open(uploaded_file)
                st.image(original_image, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True) 
                
                st.subheader("✨ 2. Processed Image")
                if os.path.exists(processed_path):
                    processed_image = Image.open(processed_path)
                    st.image(processed_image, use_container_width=True)
                    
                    st.success("success!")
                    with st.container():
                        st.download_button("💾 Download Image", open(processed_path, "rb"), "result.png", "image/png")
                else:
                    st.error("error: processed image not found")

                st.markdown("<br>", unsafe_allow_html=True) 

                st.subheader("📊 3. Extracted Data Points")
                if df is not None and not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Data as CSV",
                        data=csv,
                        file_name='extracted_data.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No data points extracted.")
                        
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
    /* 让表格容器更有层次感 */
    .stDataFrame {
        border: 1px solid #f0f2f6;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)