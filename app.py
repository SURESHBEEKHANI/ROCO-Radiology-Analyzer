import streamlit as st
from PIL import Image
import os
import base64
import io
from dotenv import load_dotenv
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ======================
# CONFIGURATION SETTINGS
# ======================
PAGE_CONFIG = {
    "page_title": "Radiology Analyzer",
    "page_icon": "🩺",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

ALLOWED_FILE_TYPES = ['png', 'jpg', 'jpeg']

CSS_STYLES = """
<style>
    .main { background-color: #f4f9f9; color: #000000; }
    .sidebar .sidebar-content { background-color: #d1e7dd; }
    .stTextInput textarea { color: #000000 !important; }
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox option,
    .stSelectbox div[role="listbox"] div {
        color: black !important;
        background-color: #d1e7dd !important;
    }
    .stSelectbox svg { fill: black !important; }
    .main-title { 
        font-size: 88px; 
        font-weight: bold; 
        color: rgb(33, 238, 238); 
    }
    .sub-title { 
        font-size: 100px; 
        color: #6B6B6B; 
        margin-top: -1px; 
    }
    .stButton>button { 
        background-color: rgb(33, 225, 250); 
        color: white; 
        font-size: 69px; 
    }
    .stImage img { 
        border-radius: 10px; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
    }
    .logo { 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .report-container {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #21eeef;
    }
    .report-text {
        font-family: 'Courier New', monospace;
        font-size: 16px;
        line-height: 1.6;
        color: #2c3e50;
    }
    .download-btn {
        background-color: #21eeef !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
    }
</style>
"""

# ======================
# CORE FUNCTIONS
# ======================
def configure_application():
    """Initialize application settings and styling"""
    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

def initialize_api_client():
    """Create and validate Groq API client"""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("API key not found. Please verify .env configuration.")
        st.stop()
    
    return Groq(api_key=api_key)

def encode_logo(image_path):
    """Encode logo image to base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except FileNotFoundError:
        st.error("Logo image not found! Using placeholder.")
        return ""

def process_image_data(uploaded_file):
    """Convert image to base64 encoded string"""
    try:
        image = Image.open(uploaded_file)
        buffer = io.BytesIO()
        image.save(buffer, format=image.format)
        return base64.b64encode(buffer.getvalue()).decode('utf-8'), image.format
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None, None

def generate_pdf_report(report_text):
    """Generate PDF document from report text"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title = Paragraph("<b>Radiology Report</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add report content
    content = Paragraph(report_text.replace('\n', '<br/>'), styles['BodyText'])
    story.append(content)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_radiology_report(uploaded_file, client):
    """Generate AI-powered radiology analysis"""
    base64_image, img_format = process_image_data(uploaded_file)
    
    if not base64_image:
        return None

    image_url = f"data:image/{img_format.lower()};base64,{base64_image}"

    try:
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "As an AI radiologist, provide a detailed structured report including: "
                        "1. Imaging modality identification\n2. Anatomical structures visualized\n"
                        "3. Abnormal findings description\n4. Differential diagnoses\n"
                        "5. Clinical correlation recommendations"
                    )},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            }],
            temperature=0.2,
            max_tokens=400,
            top_p=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API communication error: {str(e)}")
        return None

# ======================
# UI COMPONENTS
# ======================
def display_main_interface():
    """Render primary application interface"""
    # Encode logo image
    logo_b64 = encode_logo("src/radiology.png")
    
    # Center the logo and title using HTML and CSS
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div class="logo">
                <img src="data:image/png;base64,{logo_b64}" width="100">
            </div>
            <p class="main-title"> Radiology Analyzer</p>
            <p class="sub-title">Advanced Medical Imaging Analysis</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.get('analysis_result'):
            pdf_report = generate_pdf_report(st.session_state.analysis_result)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_report,
                file_name="radiology_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                help="Download formal PDF version of the report",
                key="download_pdf"
            )

    with col2:
        if st.button("Clear Analysis 🗑️", use_container_width=True, help="Remove current results"):
            st.session_state.pop('analysis_result')
            st.rerun()

    # Display analysis results
    if st.session_state.get('analysis_result'):
        st.markdown("### 🎯 Radiological Findings Report")
        st.markdown(
            f'<div class="report-container"><div class="report-text">{st.session_state.analysis_result}</div></div>', 
            unsafe_allow_html=True
        )

def render_sidebar(client):
    """Create sidebar interface elements"""
    with st.sidebar:
        st.divider()
        st.markdown("### Diagnostic Capabilities")
        st.markdown("""
        - **Multi-Modality Analysis**: X-ray, MRI, CT, Ultrasound
        - **Pathology Detection**: Fractures, tumors, infections
        - **Comparative Analysis**: Track disease progression
        - **Structured Reporting**: Standardized output format
        - **Clinical Correlation**: Suggested next steps
        """)
        st.divider()
        
        st.subheader("Image Upload Section")
        uploaded_file = st.file_uploader(
            "Select Medical Image", 
            type=ALLOWED_FILE_TYPES,
            help="Supported formats: PNG, JPG, JPEG"
        )

        if uploaded_file:
            st.image(Image.open(uploaded_file), 
                    caption="Uploaded Medical Image",
                    use_container_width=True)

            if st.button("Initiate Analysis 🔍", use_container_width=True):
                with st.spinner("Analyzing image. This may take 20-30 seconds..."):
                    report = generate_radiology_report(uploaded_file, client)
                    st.session_state.analysis_result = report
                    st.rerun()

# ======================
# APPLICATION ENTRYPOINT
# ======================
def main():
    """Primary application controller"""
    configure_application()
    groq_client = initialize_api_client()
    
    display_main_interface()
    render_sidebar(groq_client)

if __name__ == "__main__":
    main()