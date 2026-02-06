"""
Test script for database functionality
Run this to verify the database is working correctly
"""

from database import DatabaseManager
import json

def test_database():
    """Test database operations"""
    print("🧪 Testing Database Functionality\n")
    
    # Initialize database
    db = DatabaseManager("test_application_history.db")
    print("✅ Database initialized\n")
    
    # Test saving an application
    print("📝 Test 1: Saving an application...")
    test_resume_data = {
        "contact_info": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890"
        },
        "professional_summary": "Experienced software engineer...",
        "skills": {
            "technical_skills": ["Python", "JavaScript", "SQL"],
            "tools_technologies": ["Git", "Docker"],
            "methodologies": ["Agile", "TDD"]
        },
        "experience": [
            {
                "job_title": "Senior Software Engineer",
                "company": "Tech Corp",
                "dates": "2020-Present",
                "achievements": ["Built scalable APIs", "Led team of 5"]
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "University X",
                "graduation_date": "2019"
            }
        ]
    }
    
    app_id = db.save_application(
        job_description="We are looking for a Senior Python Developer...",
        resume_text="Original resume text here...",
        resume_data=test_resume_data,
        company_name="Test Company Inc",
        target_role="Senior Python Developer",
        company_info="Leading tech company in AI/ML",
        cover_letter="Dear Hiring Manager...",
        recruiter_qa=[
            {"question": "Why do you want to work here?", "answer": "I'm passionate about..."}
        ],
        model_used="gpt-4o-mini"
    )
    print(f"✅ Application saved with ID: {app_id}\n")
    
    # Test retrieving the application
    print("📖 Test 2: Retrieving the application...")
    retrieved = db.get_application(app_id)
    if retrieved:
        print(f"✅ Retrieved application: {retrieved['company_name']} - {retrieved['target_role']}")
        print(f"   Contact: {retrieved['resume_data']['contact_info']['name']}\n")
    else:
        print("❌ Failed to retrieve application\n")
    
    # Test getting all applications
    print("📚 Test 3: Getting all applications...")
    all_apps = db.get_all_applications()
    print(f"✅ Found {len(all_apps)} application(s)\n")
    
    # Test search
    print("🔍 Test 4: Searching applications...")
    search_results = db.search_applications(company_name="Test Company")
    print(f"✅ Search found {len(search_results)} result(s)\n")
    
    # Test statistics
    print("📊 Test 5: Getting statistics...")
    stats = db.get_stats()
    print(f"✅ Statistics:")
    print(f"   Total applications: {stats['total_applications']}")
    print(f"   Unique companies: {stats['unique_companies']}")
    print(f"   Unique roles: {stats['unique_roles']}")
    print(f"   Most recent: {stats['most_recent_application']}\n")
    
    # Test update
    print("✏️ Test 6: Updating application...")
    updated = db.update_application(
        app_id,
        company_name="Updated Test Company"
    )
    if updated:
        print("✅ Application updated successfully\n")
    else:
        print("❌ Failed to update application\n")
    
    # Test delete
    print("🗑️ Test 7: Deleting application...")
    deleted = db.delete_application(app_id)
    if deleted:
        print("✅ Application deleted successfully\n")
    else:
        print("❌ Failed to delete application\n")
    
    print("✨ All tests completed!")
    print("\n💡 Tip: Check 'test_application_history.db' file in your directory")

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
