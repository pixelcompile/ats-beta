"""
ATS Resume & Cover Letter Optimizer - Streamlined Version
Simple workflow: Upload PDF → Parse → LLM Optimization → Generate PDF
"""

import streamlit as st
from document_generator import DocumentGenerator
from resume_generator import ResumeGenerator
from database import DatabaseManager
import json
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(
    page_title="ATS Resume & Cover Letter Optimizer",
    page_icon="📄",
    layout="wide",
)

# Initialize database with explicit path to ensure single database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "application_history.db")
db = DatabaseManager(db_path=DB_PATH)

# Initialize session state (must be before any UI elements that access it)
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'parsed_text' not in st.session_state:
    st.session_state.parsed_text = None
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = None
if 'recruiter_qa' not in st.session_state:
    st.session_state.recruiter_qa = None
# Section visibility controls
if 'show_summary' not in st.session_state:
    st.session_state.show_summary = True
if 'show_skills' not in st.session_state:
    st.session_state.show_skills = True
if 'show_experience' not in st.session_state:
    st.session_state.show_experience = True
if 'show_projects' not in st.session_state:
    st.session_state.show_projects = True
if 'show_education' not in st.session_state:
    st.session_state.show_education = True
if 'show_certifications' not in st.session_state:
    st.session_state.show_certifications = True
# Section ordering (default order)
if 'section_order' not in st.session_state:
    st.session_state.section_order = ['summary', 'skills', 'experience', 'education', 'projects']
# Navigation state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'generator'

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📄 Wake up!</h1>', unsafe_allow_html=True)

# Sidebar for API configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Navigation menu
    st.markdown("---")
    st.header("📍 Navigation")
    page_selection = st.radio(
        "Go to:",
        options=['generator', 'history'],
        format_func=lambda x: '🚀 Resume Generator' if x == 'generator' else '📚 Application History',
        index=0 if st.session_state.current_page == 'generator' else 1,
        key='page_nav'
    )
    
    if page_selection != st.session_state.current_page:
        st.session_state.current_page = page_selection
        st.rerun()
    
    st.markdown("---")
    
    # Try to get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY', '')
    
    # Display API key status
    if api_key:
        st.success("✅ API Key Loaded")
    else:
        st.error("❌ No API Key Found")
        st.warning("Please set OPENAI_API_KEY environment variable")
    
    model = "gpt-5-nano"
    
    st.markdown("---")
    
    # Quick stats
    st.header("📊 Quick Stats")
    try:
        stats = db.get_stats()
        st.metric("Total Applications", stats['total_applications'])
        st.metric("Unique Companies", stats['unique_companies'])
        if stats['most_recent_application']:
            st.caption(f"Last application: {stats['most_recent_application']}")
    except Exception as e:
        st.caption("No application history yet")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Content")
    
    resume_content = st.text_area(
        "Paste your resume content here:",
        height=400,
        placeholder="Paste your resume text here. The app will format it professionally and generate a PDF...",
        help="Paste your resume content in plain text format. The AI will structure and format it professionally.",
    )
    
    if resume_content:
        st.session_state.parsed_text = resume_content
        st.success(f"✅ Resume content loaded ({len(resume_content)} characters)")
    else:
        resume_content = st.session_state.get('parsed_text', '')

with col2:
    st.subheader("⚙️ Options")
    
    # Font and style options
    if 'font_choice' not in st.session_state:
        st.session_state.font_choice = "Professional"
    if 'color_scheme' not in st.session_state:
        st.session_state.color_scheme = "Blue Professional"
    
    font_choice = st.selectbox(
        "Font Style:",
        ["Professional", "Modern", "Classic"],
        index=["Professional", "Modern", "Classic"].index(st.session_state.font_choice),
        help="Choose the font style for your resume"
    )
    
    color_scheme = st.selectbox(
        "Color Scheme:",
        ["Blue Professional", "Black & White", "Green Professional"],
        index=["Blue Professional", "Black & White", "Green Professional"].index(st.session_state.color_scheme),
        help="Choose the color scheme"
    )
    
    # Update session state
    st.session_state.font_choice = font_choice
    st.session_state.color_scheme = color_scheme
    
    st.markdown("---")
    
    # Quick preview
    if resume_content:
        st.markdown("### Preview")
        lines = resume_content.split('\n')[:10]
        preview_text = '\n'.join(lines)
        if len(resume_content.split('\n')) > 10:
            preview_text += '\n...'
        st.text_area("Content preview:", value=preview_text, height=150, disabled=True)

# ============================================================================
# PAGE ROUTING: Show different content based on navigation selection
# ============================================================================

if st.session_state.current_page == 'generator':
    # ======== RESUME GENERATOR PAGE ========
    st.markdown("---")

    can_generate = bool(api_key and resume_content)

    if not resume_content:
        st.warning("⚠️ Please paste your resume content")

    if st.button(
        "🎨 Format & Download Resume", 
        type="primary", 
        use_container_width=True,
        disabled=not can_generate,
        help="Format your resume content into a professional PDF and download it.",
    ):
        try:
            # Show progress
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            progress_text.text("🤖 Initializing AI optimizer...")
            progress_bar.progress(10)
            
            if not resume_content:
                st.error("Resume content is missing.")
                st.stop()

            # Initialize the resume generator
            generator = ResumeGenerator(api_key=api_key, model=model)
            
            progress_text.text("🤖 Formatting resume with AI...")
            progress_bar.progress(30)
            
            # Format the resume
            resume_data = generator.format_resume(resume_text=resume_content)
            
            progress_text.text("✅ Resume formatting complete! Validating data...")
            progress_bar.progress(60)
            
            # Validate the data
            if generator.validate_resume_data(resume_data):
                st.session_state.resume_data = resume_data
                
                progress_text.text("📄 Generating professional PDF...")
                progress_bar.progress(80)

                progress_text.text("✅ Professional resume PDF ready!")
                progress_bar.progress(100)
                
                st.success("🎉 Your professional resume is ready for download!")
                
                # Clear other session states since we're not generating cover letters
                st.session_state.cover_letter = None
                st.session_state.recruiter_qa = None
            else:
                st.error("❌ LLM returned incomplete resume data. Please try again.")
                progress_bar.empty()
                progress_text.empty()
        
        except Exception as e:
            st.error(f"❌ Error during optimization: {str(e)}")
            import traceback
            st.error("Full error details:")
            st.code(traceback.format_exc())
            progress_bar.empty()
            progress_text.empty()

    # Display optimized resume & cover letter (within generator page)
    if st.session_state.resume_data:
        st.markdown("---")
        st.subheader("✨ Your Optimized Assets")
        
        resume_data = st.session_state.resume_data
        cover_letter = st.session_state.cover_letter
        recruiter_qa = st.session_state.recruiter_qa or []

        # Build a reader-friendly base filename from first name and
        # *targeted* role/company (falling back to latest experience).
        contact = resume_data.get("contact_info", {}) or {}
        experience_list = resume_data.get("experience") or []
        target = resume_data.get("target") or {}

        full_name = (contact.get("name") or "").strip()
        first_name = full_name.split()[0] if full_name else "Resume"

        # Assume first entry in experience list is the most recent role
        if experience_list and isinstance(experience_list, list):
            latest_exp = experience_list[0] or {}
        else:
            latest_exp = {}

        # Prefer explicit targeting metadata over inferred experience
        role = (target.get("role_title") or "").strip() or (latest_exp.get("job_title") or "").strip() or "Role"
        company = (target.get("company_name") or "").strip() or (latest_exp.get("company") or "").strip() or "Company"

        # Join parts with underscores and strip internal extra whitespace
        def _slugify_part(value: str, fallback: str) -> str:
            cleaned = "_".join(value.split()) if value else fallback
            return cleaned or fallback

        first_name_part = _slugify_part(first_name, "Resume")
        role_part = _slugify_part(role, "Role")
        company_part = _slugify_part(company, "Company")

        base_filename = f"{first_name_part}_{role_part}_{company_part}"
    
        # Create tabs for different views
        overview_tab, resume_tab, data_tab = st.tabs([
            "📊 Overview",
            "📄 Resume",
            "🔧 Data",
        ])
    
        with overview_tab:
            st.markdown("### Overview")
            st.markdown("Your professionally formatted resume is ready!")

            # Simple summary cards
            col_ov_1, col_ov_2 = st.columns(2)
            with col_ov_1:
                st.markdown("#### Candidate")
                if contact.get('name'):
                    st.markdown(f"**Name:** {contact['name']}")
                st.markdown(f"**Status:** ✅ Resume formatted")

            with col_ov_2:
                st.markdown("#### Download")
                st.markdown("Your professional resume PDF is ready for download below.")

            st.markdown("---")
            st.markdown("#### Download Your Resume")
            try:
                pdf_buffer = DocumentGenerator.create_pdf_from_json(
                    resume_data,
                    show_summary=st.session_state.show_summary,
                    show_skills=st.session_state.show_skills,
                    show_experience=st.session_state.show_experience,
                    show_projects=st.session_state.show_projects,
                    show_education=st.session_state.show_education,
                    show_certifications=st.session_state.show_certifications,
                    section_order=st.session_state.section_order,
                    font_choice=st.session_state.font_choice,
                    color_scheme=st.session_state.color_scheme
                )
                st.download_button(
                    label="📄 Download Professional Resume (PDF)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"{base_filename}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error generating resume PDF: {str(e)}")

        with resume_tab:
            # Add edit mode toggle
            col_header1, col_header2 = st.columns([3, 1])
            with col_header1:
                st.markdown("### Resume Preview & Editor")
            with col_header2:
                if 'edit_mode' not in st.session_state:
                    st.session_state.edit_mode = False
            
                if st.button("✏️ Edit" if not st.session_state.edit_mode else "👁️ Preview", 
                            use_container_width=True):
                    st.session_state.edit_mode = not st.session_state.edit_mode
                    st.rerun()
        
            if st.session_state.edit_mode:
                st.info("✏️ **Edit Mode Active** - Make your changes below and click 'Save Changes' to update your resume.")
            
                # Section visibility controls
                st.markdown("#### 📋 Section Management")
                st.caption("Toggle sections on/off and reorder them. Disabled sections won't appear in your resume.")
            
                # Section visibility checkboxes
                st.markdown("**Section Visibility:**")
                col_sec1, col_sec2, col_sec3 = st.columns(3)
                with col_sec1:
                    show_summary = st.checkbox("Professional Summary", value=st.session_state.show_summary, key="checkbox_summary")
                    show_skills = st.checkbox("Skills", value=st.session_state.show_skills, key="checkbox_skills")
                with col_sec2:
                    show_experience = st.checkbox("Experience", value=st.session_state.show_experience, key="checkbox_experience")
                    show_projects = st.checkbox("Projects", value=st.session_state.show_projects, key="checkbox_projects")
                with col_sec3:
                    show_education = st.checkbox("Education", value=st.session_state.show_education, key="checkbox_education")
                    show_certifications = st.checkbox("Certifications", value=st.session_state.show_certifications, key="checkbox_certifications")
            
                # Section ordering
                st.markdown("**Section Order:**")
                st.caption("Drag to reorder or use the select box to set the display order of sections in your resume.")
            
                section_labels = {
                    'summary': '📝 Professional Summary',
                    'skills': '🛠️ Skills',
                    'experience': '💼 Experience',
                    'projects': '🚀 Projects',
                    'education': '🎓 Education',
                    'certifications': '📜 Certifications'
                }
            
                # Create a reorderable list using selectbox for each position
                new_order = st.session_state.section_order.copy()
            
                st.markdown("*Select the section for each position (1 = top, 6 = bottom):*")
                col_order1, col_order2, col_order3 = st.columns(3)
            
                with col_order1:
                    pos1 = st.selectbox("Position 1 (Top)", 
                                       options=list(section_labels.keys()),
                                       format_func=lambda x: section_labels[x],
                                       index=list(section_labels.keys()).index(new_order[0]) if len(new_order) > 0 else 0,
                                       key="order_pos_1")
                    pos2 = st.selectbox("Position 2", 
                                       options=list(section_labels.keys()),
                                       format_func=lambda x: section_labels[x],
                                       index=list(section_labels.keys()).index(new_order[1]) if len(new_order) > 1 else 1,
                                       key="order_pos_2")
            
                with col_order2:
                    pos3 = st.selectbox("Position 3", 
                                       options=list(section_labels.keys()),
                                       format_func=lambda x: section_labels[x],
                                       index=list(section_labels.keys()).index(new_order[2]) if len(new_order) > 2 else 2,
                                       key="order_pos_3")
                    pos4 = st.selectbox("Position 4", 
                                       options=list(section_labels.keys()),
                                       format_func=lambda x: section_labels[x],
                                       index=list(section_labels.keys()).index(new_order[3]) if len(new_order) > 3 else 3,
                                       key="order_pos_4")
            
                with col_order3:
                    pos5 = st.selectbox("Position 5", 
                                       options=list(section_labels.keys()),
                                       format_func=lambda x: section_labels[x],
                                       index=list(section_labels.keys()).index(new_order[4]) if len(new_order) > 4 else 4,
                                       key="order_pos_5")
                    pos6 = st.selectbox("Position 6 (Bottom)", 
                                       options=list(section_labels.keys()),
                                       format_func=lambda x: section_labels[x],
                                       index=list(section_labels.keys()).index(new_order[5]) if len(new_order) > 5 else 5,
                                       key="order_pos_6")
            
                selected_order = [pos1, pos2, pos3, pos4, pos5, pos6]
            
                # Check for duplicates and show warning
                if len(selected_order) != len(set(selected_order)):
                    st.warning("⚠️ Each section can only appear once. Please select different sections for each position.")
            
                st.markdown("---")
            
                # Create a form for editing
                with st.form("resume_edit_form"):
                    # Contact Info
                    st.markdown("#### Contact Information")
                    contact = resume_data.get('contact_info', {})
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Name", value=contact.get('name', ''))
                        new_email = st.text_input("Email", value=contact.get('email', ''))
                    with col2:
                        new_phone = st.text_input("Phone", value=contact.get('phone', ''))
                        new_location = st.text_input("Location", value=contact.get('location', ''))
                
                    new_linkedin = st.text_input("LinkedIn (optional)", value=contact.get('linkedin', ''))
                
                    # Professional Summary
                    st.markdown("#### Professional Summary")
                    new_summary = st.text_area("Professional Summary", 
                                              value=resume_data.get('professional_summary', ''),
                                              height=150)
                
                    # Skills
                    st.markdown("#### Skills")
                    skills = resume_data.get('skills', {})
                    tech_skills_text = ', '.join(skills.get('technical_skills', []))
                    tools_text = ', '.join(skills.get('tools_technologies', []))
                    methods_text = ', '.join(skills.get('methodologies', []))
                
                    new_tech_skills = st.text_area("Technical Skills (comma-separated)", value=tech_skills_text, height=80)
                    new_tools = st.text_area("Tools & Technologies (comma-separated)", value=tools_text, height=80)
                    new_methods = st.text_area("Methodologies (comma-separated)", value=methods_text, height=80)
                
                    # Experience
                    st.markdown("#### Professional Experience")
                    experience_list = resume_data.get('experience', [])
                
                    new_experience = []
                
                    for idx, job in enumerate(experience_list):
                        col_exp_header, col_exp_remove = st.columns([4, 1])
                        with col_exp_header:
                            exp_label = f"Experience Entry {idx + 1}: {job.get('job_title', 'N/A')}"
                        with col_exp_remove:
                            remove_exp = st.checkbox(f"Remove", key=f"remove_exp_{idx}", help="Check to remove this entry")
                    
                        if not remove_exp:
                            with st.expander(exp_label, expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    job_title = st.text_input(f"Job Title {idx}", value=job.get('job_title', ''), key=f"exp_title_{idx}")
                                    company = st.text_input(f"Company {idx}", value=job.get('company', ''), key=f"exp_company_{idx}")
                                with col2:
                                    location = st.text_input(f"Location {idx}", value=job.get('location', ''), key=f"exp_loc_{idx}")
                                    dates = st.text_input(f"Dates {idx}", value=job.get('dates', ''), key=f"exp_dates_{idx}")
                            
                                # Achievements
                                achievements_text = "\n".join(job.get('achievements', []))
                                achievements_input = st.text_area(
                                    f"Achievements (one per line) {idx}",
                                    value=achievements_text,
                                    height=150,
                                    key=f"exp_achievements_{idx}"
                                )
                                achievements = [a.strip() for a in achievements_input.split('\n') if a.strip()]
                            
                                new_experience.append({
                                    'job_title': job_title,
                                    'company': company,
                                    'location': location,
                                    'dates': dates,
                                    'achievements': achievements
                                })
                
                    # Projects (Simple format - 2-3 lines)
                    st.markdown("#### Projects")
                    projects_list = resume_data.get('projects', [])
                
                    new_projects = []
                
                    for idx, proj in enumerate(projects_list):
                        col_proj_header, col_proj_remove = st.columns([4, 1])
                        with col_proj_header:
                            proj_label = f"Project {idx + 1}: {proj.get('project_name', 'N/A')}"
                        with col_proj_remove:
                            remove_proj = st.checkbox(f"Remove", key=f"remove_proj_{idx}", help="Check to remove this project")
                    
                        if not remove_proj:
                            with st.expander(proj_label, expanded=False):
                                project_name = st.text_input(f"Project Name {idx}", value=proj.get('project_name', ''), key=f"proj_name_{idx}")
                                project_company = st.text_input(f"Company {idx}", value=proj.get('company', ''), key=f"proj_company_{idx}", help="Must match a company from Experience")
                            
                                # Bullet points (like experience achievements)
                                bullets_text = "\n".join(proj.get('bullets', []))
                                # Fallback to description if bullets don't exist
                                if not bullets_text and proj.get('description'):
                                    bullets_text = proj.get('description')
                            
                                bullets_input = st.text_area(
                                    f"Bullet Points (one per line, 2-3 bullets) {idx}",
                                    value=bullets_text,
                                    height=100,
                                    key=f"proj_bullets_{idx}",
                                    help="Example:\nDesigned and implemented React/Redux dashboard consuming REST APIs, improving data fetch efficiency by 14%\nBuilt real-time visualization using D3.js and WebSocket connections"
                                )
                                bullets = [b.strip() for b in bullets_input.split('\n') if b.strip()]
                            
                                new_projects.append({
                                    'project_name': project_name,
                                    'company': project_company,
                                    'bullets': bullets
                                })
                
                    # Education
                    st.markdown("#### Education")
                    education_list = resume_data.get('education', [])
                
                    new_education = []
                
                    for idx, edu in enumerate(education_list):
                        col_edu_header, col_edu_remove = st.columns([4, 1])
                        with col_edu_header:
                            edu_label = f"Education Entry {idx + 1}"
                        with col_edu_remove:
                            remove_edu = st.checkbox(f"Remove", key=f"remove_edu_{idx}", help="Check to remove this entry")
                    
                        if not remove_edu:
                            with st.expander(edu_label, expanded=True):
                                col1, col2 = st.columns(2)
                                with col1:
                                    degree = st.text_input(f"Degree {idx}", value=edu.get('degree', ''), key=f"edu_degree_{idx}")
                                    institution = st.text_input(f"Institution {idx}", value=edu.get('institution', ''), key=f"edu_inst_{idx}")
                                with col2:
                                    location = st.text_input(f"Location {idx}", value=edu.get('location', ''), key=f"edu_loc_{idx}")
                                    grad_date = st.text_input(f"Graduation Date {idx}", value=edu.get('graduation_date', ''), key=f"edu_date_{idx}")
                                gpa = st.text_input(f"GPA (optional) {idx}", value=edu.get('gpa', ''), key=f"edu_gpa_{idx}")
                            
                                new_education.append({
                                    'degree': degree,
                                    'institution': institution,
                                    'location': location,
                                    'graduation_date': grad_date,
                                    'gpa': gpa if gpa else None
                                })
                
                    # Certifications
                    st.markdown("#### Certifications")
                    cert_list = resume_data.get('certifications', [])
                
                    new_certifications = []
                
                    for idx, cert in enumerate(cert_list):
                        col_cert_header, col_cert_remove = st.columns([4, 1])
                        with col_cert_header:
                            cert_label = f"Certification {idx + 1}"
                        with col_cert_remove:
                            remove_cert = st.checkbox(f"Remove", key=f"remove_cert_{idx}", help="Check to remove this certification")
                    
                        if not remove_cert:
                            with st.expander(cert_label, expanded=False):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    cert_name = st.text_input(f"Name {idx}", value=cert.get('name', ''), key=f"cert_name_{idx}")
                                with col2:
                                    cert_issuer = st.text_input(f"Issuer {idx}", value=cert.get('issuer', ''), key=f"cert_issuer_{idx}")
                                with col3:
                                    cert_date = st.text_input(f"Date {idx}", value=cert.get('date', ''), key=f"cert_date_{idx}")
                            
                                new_certifications.append({
                                    'name': cert_name,
                                    'issuer': cert_issuer,
                                    'date': cert_date
                                })
                
                    # Submit button
                    submitted = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                
                    if submitted:
                        # Update section visibility
                        st.session_state.show_summary = show_summary
                        st.session_state.show_skills = show_skills
                        st.session_state.show_experience = show_experience
                        st.session_state.show_projects = show_projects
                        st.session_state.show_education = show_education
                        st.session_state.show_certifications = show_certifications
                    
                        # Update section order (only if no duplicates)
                        if len(selected_order) == len(set(selected_order)):
                            st.session_state.section_order = selected_order
                    
                        # Update resume_data with edited values (only include non-empty fields)
                        contact_info = {}
                        if new_name and new_name.strip():
                            contact_info['name'] = new_name.strip()
                        if new_email and new_email.strip():
                            contact_info['email'] = new_email.strip()
                        if new_phone and new_phone.strip():
                            contact_info['phone'] = new_phone.strip()
                        if new_location and new_location.strip():
                            contact_info['location'] = new_location.strip()
                        if new_linkedin and new_linkedin.strip():
                            contact_info['linkedin'] = new_linkedin.strip()
                    
                        st.session_state.resume_data['contact_info'] = contact_info
                        st.session_state.resume_data['professional_summary'] = new_summary
                        st.session_state.resume_data['education'] = new_education
                        st.session_state.resume_data['certifications'] = new_certifications
                        st.session_state.resume_data['experience'] = new_experience
                        st.session_state.resume_data['projects'] = new_projects
                        st.session_state.resume_data['skills'] = {
                            'technical_skills': [s.strip() for s in new_tech_skills.split(',') if s.strip()],
                            'tools_technologies': [s.strip() for s in new_tools.split(',') if s.strip()],
                            'methodologies': [s.strip() for s in new_methods.split(',') if s.strip()]
                        }
                    
                        st.success("✅ Resume updated successfully! Switch to Preview mode to see your changes.")
                        st.session_state.edit_mode = False
                        st.rerun()
        
            else:
                # Preview Mode (read-only display)
                st.info("👁️ **Preview Mode** - Click 'Edit' to modify your resume.")
            
                # Contact Info
                contact = resume_data.get('contact_info', {})
                if contact and contact.get('name'):
                    st.markdown(f"## {contact['name']}")
            
                # Only display non-empty contact fields
                contact_parts = []
                if contact:
                    if contact.get('email') and contact.get('email').strip():
                        contact_parts.append(f"📧 {contact['email'].strip()}")
                    if contact.get('phone') and contact.get('phone').strip():
                        contact_parts.append(f"📱 {contact['phone'].strip()}")
                    if contact.get('location') and contact.get('location').strip():
                        contact_parts.append(f"📍 {contact['location'].strip()}")
            
                if contact_parts:
                    st.markdown(" | ".join(contact_parts))
            
                # Display sections in user-defined order
                def render_section(section_name):
                    """Render a section based on its name"""
                    if section_name == 'summary' and st.session_state.show_summary and resume_data.get('professional_summary'):
                        st.markdown("### Professional Summary")
                        st.markdown(resume_data['professional_summary'])
                
                    elif section_name == 'skills' and st.session_state.show_skills and resume_data.get('skills'):
                        st.markdown("### Skills")
                        skills = resume_data['skills']
                        all_skills = []
                        if skills.get('technical_skills'):
                            all_skills.extend(skills['technical_skills'])
                        if skills.get('tools_technologies'):
                            all_skills.extend(skills['tools_technologies'])
                        if skills.get('methodologies'):
                            all_skills.extend(skills['methodologies'])
                        if all_skills:
                            st.markdown(", ".join(all_skills))
                
                    elif section_name == 'experience' and st.session_state.show_experience and resume_data.get('experience'):
                        st.markdown("### Professional Experience")
                        for job in resume_data['experience']:
                            st.markdown(f"**{job.get('job_title', 'N/A')}** - {job.get('company', 'N/A')}")
                            st.markdown(f"*{job.get('location', '')} | {job.get('dates', '')}*")
                            if job.get('achievements'):
                                for achievement in job['achievements']:
                                    st.markdown(f"- {achievement}")
                            st.markdown("")
                
                    elif section_name == 'projects' and st.session_state.show_projects and resume_data.get('projects'):
                        st.markdown("### Projects")
                        for project in resume_data['projects']:
                            st.markdown(f"**{project.get('project_name', 'N/A')}**")
                            # Display bullets
                            if project.get('bullets'):
                                for bullet in project['bullets']:
                                    st.markdown(f"- {bullet}")
                            # Fallback to description (backward compatibility)
                            elif project.get('description'):
                                st.markdown(f"- {project['description']}")
                            st.markdown("")
                
                    elif section_name == 'education' and st.session_state.show_education and resume_data.get('education'):
                        st.markdown("### Education")
                        for edu in resume_data['education']:
                            st.markdown(f"**{edu.get('degree', 'N/A')}** - {edu.get('institution', 'N/A')}")
                            edu_parts = []
                            if edu.get('location'):
                                edu_parts.append(edu['location'])
                            if edu.get('graduation_date'):
                                edu_parts.append(edu['graduation_date'])
                            if edu_parts:
                                st.markdown(" | ".join(edu_parts))
                
                    elif section_name == 'certifications' and st.session_state.show_certifications and resume_data.get('certifications'):
                        st.markdown("### Certifications")
                        for cert in resume_data['certifications']:
                            st.markdown(f"- **{cert.get('name', 'N/A')}** - {cert.get('issuer', 'N/A')} ({cert.get('date', 'N/A')})")
            
                # Render sections in the user-defined order
                for section_name in st.session_state.section_order:
                    render_section(section_name)

            st.markdown("---")
            st.markdown("#### Download Resume")
            col_res_dl1, col_res_dl2, col_res_dl3 = st.columns(3)
            with col_res_dl1:
                try:
                    pdf_buffer = DocumentGenerator.create_pdf_from_json(
                        resume_data,
                        show_summary=st.session_state.show_summary,
                        show_skills=st.session_state.show_skills,
                        show_experience=st.session_state.show_experience,
                        show_projects=st.session_state.show_projects,
                        show_education=st.session_state.show_education,
                        show_certifications=st.session_state.show_certifications,
                        section_order=st.session_state.section_order,
                        font_choice=st.session_state.font_choice,
                        color_scheme=st.session_state.color_scheme
                    )
                    st.download_button(
                        label="📄 PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"{base_filename}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error generating resume PDF: {str(e)}")

            with col_res_dl2:
                try:
                    docx_buffer = DocumentGenerator.create_docx_from_json(
                        resume_data,
                        show_summary=st.session_state.show_summary,
                        show_skills=st.session_state.show_skills,
                        show_experience=st.session_state.show_experience,
                        show_projects=st.session_state.show_projects,
                        show_education=st.session_state.show_education,
                        show_certifications=st.session_state.show_certifications,
                        section_order=st.session_state.section_order
                    )
                    st.download_button(
                        label="📝 DOCX",
                        data=docx_buffer.getvalue(),
                        file_name=f"{base_filename}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error generating resume DOCX: {str(e)}")

            with col_res_dl3:
                json_str = json.dumps(resume_data, indent=2)
                st.download_button(
                    label="📋 JSON",
                    data=json_str,
                    file_name=f"{base_filename}.json",
                    mime="application/json",
                    use_container_width=True,
                )
    
        with data_tab:
            st.markdown("### Raw Data (JSON)")
            st.write("Resume structure returned by the model:")
            st.json(resume_data)

elif st.session_state.current_page == 'history':
    # ======== APPLICATION HISTORY PAGE ========
    st.subheader("📚 Application History")
    
    try:
        all_applications = db.get_all_applications()
        
        if not all_applications:
            st.info("📝 No saved applications yet. Generate your first resume to start building your history!")
            st.markdown("")
            if st.button("🚀 Go to Resume Generator", use_container_width=True, type="primary"):
                st.session_state.current_page = 'generator'
                st.rerun()
        else:
            # Show statistics
            stats = db.get_stats()
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Total Applications", stats['total_applications'])
            with col_stat2:
                st.metric("Unique Companies", stats['unique_companies'])
            with col_stat3:
                st.metric("Unique Roles", stats['unique_roles'])
            
            st.markdown("---")
            
            # Search and filter
            st.markdown("#### Search & Filter")
            col_search1, col_search2 = st.columns(2)
            with col_search1:
                search_company = st.text_input("🏢 Search by Company", placeholder="Enter company name...", key="hist_search_company")
            with col_search2:
                search_role = st.text_input("💼 Search by Role", placeholder="Enter role title...", key="hist_search_role")
            
            # Apply filters
            if search_company or search_role:
                filtered_applications = db.search_applications(
                    company_name=search_company if search_company else None,
                    target_role=search_role if search_role else None
                )
                st.markdown(f"*Found {len(filtered_applications)} matching applications*")
                display_applications = filtered_applications
            else:
                display_applications = all_applications
            
            # Display applications
            st.markdown("---")
            st.markdown("#### Saved Applications")
            
            for app in display_applications:
                with st.expander(
                    f"📄 {app.get('company_name', 'Unknown Company')} - {app.get('target_role', 'Unknown Role')} ({app.get('created_at', 'Unknown date')})",
                    expanded=False
                ):
                    col_app1, col_app2 = st.columns([3, 1])
                    
                    with col_app1:
                        st.markdown(f"**Company:** {app.get('company_name', 'N/A')}")
                        st.markdown(f"**Role:** {app.get('target_role', 'N/A')}")
                        st.markdown(f"**Model Used:** {app.get('model_used', 'N/A')}")
                        st.markdown(f"**Created:** {app.get('created_at', 'N/A')}")
                        
                        if app.get('company_info'):
                            with st.expander("📋 Company Info", expanded=False):
                                st.write(app['company_info'])
                        
                        with st.expander("💼 Job Description", expanded=False):
                            st.write(app.get('job_description', 'N/A'))
                    
                    with col_app2:
                        # Action buttons
                        if st.button("🔄 Load", key=f"hist_load_{app['id']}", help="Load this application into the current session"):
                            try:
                                # Load into session state
                                st.session_state.resume_data = app['resume_data']
                                st.session_state.cover_letter = app.get('cover_letter')
                                st.session_state.recruiter_qa = app.get('recruiter_qa', [])
                                st.session_state.parsed_text = app.get('resume_text')
                                # Switch to generator page to show the loaded data
                                st.session_state.current_page = 'generator'
                                st.success(f"✅ Loaded application #{app['id']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error loading application: {str(e)}")
                        
                        if st.button("🗑️ Delete", key=f"hist_delete_{app['id']}", help="Delete this application"):
                            if db.delete_application(app['id']):
                                st.success("✅ Application deleted")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete")
                    
                    # Download options for this historical application
                    st.markdown("---")
                    st.markdown("**Download Options:**")
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    
                    with col_dl1:
                        # Resume PDF
                        try:
                            app_resume_data = app['resume_data']
                            if app_resume_data:
                                pdf_buffer = DocumentGenerator.create_pdf_from_json(app_resume_data)
                                
                                # Generate filename from app data
                                contact = app_resume_data.get('contact_info', {}) or {}
                                first_name = (contact.get('name') or '').split()[0] if contact.get('name') else 'Resume'
                                app_company = app.get('company_name', 'Company')
                                app_role = app.get('target_role', 'Role')
                                app_filename = f"{first_name}_{app_role}_{app_company}".replace(' ', '_')
                                
                                st.download_button(
                                    label="📄 Resume PDF",
                                    data=pdf_buffer.getvalue(),
                                    file_name=f"{app_filename}.pdf",
                                    mime="application/pdf",
                                    key=f"hist_dl_resume_{app['id']}",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.caption(f"Resume unavailable: {str(e)}")
                    
                    with col_dl2:
                        # Cover Letter PDF
                        if app.get('cover_letter'):
                            try:
                                app_resume_data = app['resume_data']
                                contact = app_resume_data.get('contact_info', {}) or {}
                                app_company = app.get('company_name', 'Company')
                                app_role = app.get('target_role', 'Role')
                                first_name = (contact.get('name') or '').split()[0] if contact.get('name') else 'Resume'
                                app_filename = f"{first_name}_{app_role}_{app_company}".replace(' ', '_')
                                
                                cover_pdf = DocumentGenerator.create_cover_letter_pdf(
                                    cover_letter_text=app['cover_letter'],
                                    candidate_name=contact.get('name'),
                                    company_name=app.get('company_name'),
                                    role_title=app.get('target_role')
                                )
                                st.download_button(
                                    label="✉️ Cover Letter",
                                    data=cover_pdf.getvalue(),
                                    file_name=f"{app_filename}_CoverLetter.pdf",
                                    mime="application/pdf",
                                    key=f"hist_dl_cover_{app['id']}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.caption(f"Cover letter unavailable: {str(e)}")
                    
                    with col_dl3:
                        # Full JSON export
                        json_export = {
                            'company_name': app.get('company_name'),
                            'target_role': app.get('target_role'),
                            'job_description': app.get('job_description'),
                            'company_info': app.get('company_info'),
                            'resume_data': app.get('resume_data'),
                            'cover_letter': app.get('cover_letter'),
                            'recruiter_qa': app.get('recruiter_qa'),
                            'created_at': app.get('created_at')
                        }
                        st.download_button(
                            label="📋 JSON Export",
                            data=json.dumps(json_export, indent=2),
                            file_name=f"{app_filename}_full_export.json",
                            mime="application/json",
                            key=f"hist_dl_json_{app['id']}",
                            use_container_width=True
                        )
    
    except Exception as e:
        st.error(f"❌ Error loading history: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Made with ❤️ using Streamlit & OpenAI</p>
    </div>
""", unsafe_allow_html=True)
