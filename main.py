"""
Simple Resume Formatter

This lightweight app accepts raw resume text, preserves the content, and generates
a downloadable PDF without modifying the text.
"""

import streamlit as st
from document_generator import DocumentGenerator

st.set_page_config(page_title="Resume Formatter", page_icon="📄", layout="wide")

st.title("Resume Formatter — Paste and download as PDF")

resume_text = st.text_area(
    "Paste your resume text here (plain text). Do not include API keys or secrets.",
    height=500,
)

col1, col2 = st.columns(2)
with col1:
    font_choice = st.selectbox("Font style", ["Professional", "Modern", "Classic"], index=0)
with col2:
    color_scheme = st.selectbox(
        "Color scheme (affects styling)", ["Blue Professional", "Black & White", "Green Professional"], index=0
    )

if resume_text:
    st.markdown("**Preview (first 30 lines)**")
    preview = "\n".join(resume_text.split("\n")[:30])
    if len(resume_text.split("\n")) > 30:
        preview += "\n..."
    st.text_area("Preview", value=preview, height=200, disabled=True)

if st.button("Format & Download PDF", disabled=not bool(resume_text)):
    try:
        pdf_buffer = DocumentGenerator.create_pdf_from_text(
            resume_text, font_choice=font_choice, color_scheme=color_scheme
        )
        st.success("PDF generated — click the button below to download.")
        st.download_button(
            label="Download PDF",
            data=pdf_buffer.getvalue(),
            file_name="resume.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
    
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
