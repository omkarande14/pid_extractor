import os
import json
import io
import pandas as pd
from PIL import Image
import fitz  # PyMuPDF (No Poppler required!)
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load environment variables
load_dotenv()

# Set up Streamlit page configuration
st.set_page_config(
    page_title="P&ID Engineering Data Extractor",
    page_icon="🛠️",
    layout="wide"
)

# Application Header
st.title("🛠️ P&ID & PFD Component Extractor")
st.markdown("Upload a technical drawing (**PDF, PNG, JPG, JPEG**) to extract engineering components into a downloadable Excel sheet.")

# Sidebar Configuration
st.sidebar.header("Configuration")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.warning("⚠️ Please configure `GEMINI_API_KEY` in your `.env` file or enter it in the sidebar.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# 2. File Upload Workbench
uploaded_file = st.file_uploader(
    "Choose a P&ID or PFD Diagram File (PDF or Image)", 
    type=["pdf", "png", "jpg", "jpeg", "bmp"]
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    image_to_process = None

    # Handle PDF Input using PyMuPDF (Zero-Dependency)
    if uploaded_file.name.lower().endswith(".pdf"):
        st.info("📄 PDF file detected. Rendering page into high-res image...")
        try:
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            page = pdf_doc.load_page(0)  # Load Page 1
            
            # Render page to 200 DPI image
            pix = page.get_pixmap(dpi=200)
            image_to_process = Image.open(io.BytesIO(pix.tobytes("png")))
            pdf_doc.close()
        except Exception as e:
            st.error(f"❌ Error processing PDF: {e}")
            st.stop()
    else:
        # Handle Standard Image Input
        image_to_process = Image.open(io.BytesIO(file_bytes))

    # Show side-by-side view (Preview on Left, Extraction Options on Right)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🖼️ Diagram Preview")
        st.image(image_to_process, use_container_width=True, caption=uploaded_file.name)
        
    with col2:
        st.subheader("⚡ AI Processing")
        st.write("Ready to extract components: Pumps, Tanks, Valves, Pipelines, and Instruments.")
        
        process_btn = st.button("🚀 Extract Data with Gemini AI", type="primary")

    # 3. Extraction Logic
    if process_btn:
        with st.spinner("Analyzing diagram with Gemini AI Vision... Please wait..."):
            
            prompt = """
            You are an AI specialized in reading P&ID and PFD technical engineering drawings.
            Analyze the uploaded image and extract all engineering components (Pumps, Tanks, Valves, Instruments, Pipe Lines).
            
            Return a JSON array containing objects with the following schema:
            [
                {
                    "Tag_Number": "P-101",
                    "Component_Type": "Pump",
                    "Line_Size": "4\"",
                    "Description": "Raw Water Pump",
                    "Connected_From_To": "TK-101 -> V-101"
                }
            ]
            """
            
            try:
                # Call Gemini API
                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=[image_to_process, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                # Parse JSON and create DataFrame
                data = json.loads(response.text)
                df = pd.DataFrame(data)

                st.success("✅ Extraction Complete!")

                # 4. Data Preview & Download Section
                st.markdown("---")
                st.subheader("📊 Extracted Engineering Data")
                
                # Interactive Table
                st.dataframe(df, use_container_width=True)

                # Convert DataFrame to Excel in-memory buffer
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Components")
                
                excel_bytes = excel_buffer.getvalue()
                
                # Clean output filename based on uploaded file
                base_name = os.path.splitext(uploaded_file.name)[0]
                output_excel_name = f"Extracted_{base_name}.xlsx"

                # Download Button
                st.download_button(
                    label="📥 Download Excel Sheet (.xlsx)",
                    data=excel_bytes,
                    file_name=output_excel_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

            except Exception as e:
                st.error(f"❌ Error during extraction: {e}")