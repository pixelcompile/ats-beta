"""
Resume Formatter - LLM-powered professional formatting with PDF export
"""

import streamlit as st
from document_generator import DocumentGenerator
from resume_generator import ResumeGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Resume Formatter", page_icon="📄", layout="wide")

st.title("📄 Professional Resume Formatter")
st.markdown("Paste your resume text. LLM analyzes and formats it professionally as PDF.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = os.getenv('OPENAI_API_KEY', '')
    
    if api_key:
        st.success("✅ OpenAI API Key Loaded")
    else:
        st.error("❌ No OpenAI API Key Found")
        st.info("Set the `OPENAI_API_KEY` environment variable")
    
    st.markdown("---")
    # style selectors live here so they can be changed anytime
    font_choice = st.selectbox("Font Style", ["Professional", "Modern", "Classic"], index=0)
    color_scheme = st.selectbox(
        "Color Scheme",
        ["Blue Professional", "Black & White", "Green Professional"],
        index=0
    )

# Main content
col_input, col_preview = st.columns([1.5, 1])

with col_input:
    st.subheader("📝 Resume Input")
    resume_text = st.text_area(
        "Paste your resume (plain text):",
        height=450,
        placeholder="John Doe\nEmail: john@example.com\nPhone: 555-1234\n\nProfessional Summary:\nExperienced software engineer...",
    )

with col_preview:
    st.subheader("📋 Preview")
    if resume_text:
        preview_lines = resume_text.split("\n")[:20]
        preview = "\n".join(preview_lines)
        if len(resume_text.split("\n")) > 20:
            preview += "\n..."
        st.text_area("Preview (first 20 lines):", value=preview, height=450, disabled=True)
    else:
        st.info("Resume preview appears here")

st.markdown("---")

# Format button invokes only LLM classification and stores data
can_generate = bool(api_key and resume_text)

if st.button(
    "🤖 Analyze Resume",
    type="primary",
    use_container_width=True,
    disabled=not can_generate,
):
    if not resume_text:
        st.error("❌ Please paste your resume content")
        st.stop()
    
    if not api_key:
        st.error("❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        st.stop()
    
    try:
        progress_text = st.empty()
        progress_bar = st.progress(0)
        progress_text.text("🤖 Initializing AI resume formatter...")
        progress_bar.progress(10)

        generator = ResumeGenerator(api_key=api_key, model="gpt-4o-mini")
        progress_text.text("🔍 Classifying resume sections...")
        progress_bar.progress(40)

        resume_data = generator.format_resume(resume_text=resume_text)

        progress_text.text("✅ Validating classification...")
        progress_bar.progress(70)

        if not generator.validate_resume_data(resume_data):
            st.error("❌ Resume validation failed. Please check the input and try again.")
            progress_bar.empty()
            progress_text.empty()
            st.stop()

        st.session_state.resume_data = resume_data
        st.success("✅ Resume classified and stored. You can now adjust style and download.")
        progress_bar.empty()
        progress_text.empty()
    except Exception as e:
        st.error(f"❌ Error during classification: {str(e)}")
        import traceback
        with st.expander("📋 Technical Details"):
            st.code(traceback.format_exc(), language="python")

# After classification show formatting & download section
if 'resume_data' in st.session_state and st.session_state.resume_data:
    st.markdown("---")
    st.subheader("🎨 Format & Download")
    try:
        pdf_buffer = DocumentGenerator.create_pdf_from_json(
            st.session_state.resume_data,
            show_summary=True,
            show_skills=True,
            show_experience=True,
            show_projects=True,
            show_education=True,
            show_certifications=True,
            section_order=['summary','skills','experience','education','projects'],
            font_choice=font_choice,
            color_scheme=color_scheme
        )
        contact = st.session_state.resume_data.get('contact_info', {})
        name = contact.get('name', 'Resume').replace(' ', '_')
        st.download_button(
            label="📥 Download PDF with current style",
            data=pdf_buffer.getvalue(),
            file_name=f"{name}_resume.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")

