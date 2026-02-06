"""
Database Manager for Application History
Stores job applications, resumes, cover letters, and related data
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database operations for application history"""
    
    def __init__(self, db_path: str = "application_history.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                target_role TEXT,
                job_description TEXT NOT NULL,
                company_info TEXT,
                resume_text TEXT NOT NULL,
                resume_data TEXT NOT NULL,
                cover_letter TEXT,
                recruiter_qa TEXT,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on company_name and target_role for faster searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_role 
            ON applications(company_name, target_role)
        """)
        
        # Create index on created_at for chronological queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON applications(created_at DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def save_application(
        self,
        job_description: str,
        resume_text: str,
        resume_data: Dict,
        company_name: Optional[str] = None,
        target_role: Optional[str] = None,
        company_info: Optional[str] = None,
        cover_letter: Optional[str] = None,
        recruiter_qa: Optional[List[Dict]] = None,
        model_used: Optional[str] = None
    ) -> int:
        """
        Save an application to the database.
        
        Args:
            job_description: The job description text
            resume_text: Original resume text (extracted from PDF)
            resume_data: Structured resume data (as JSON-serializable dict)
            company_name: Target company name
            target_role: Target role/position title
            company_info: Additional company information
            cover_letter: Generated cover letter text
            recruiter_qa: List of recruiter Q&A pairs
            model_used: AI model used for generation
            
        Returns:
            int: ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize complex objects to JSON
        resume_data_json = json.dumps(resume_data)
        recruiter_qa_json = json.dumps(recruiter_qa) if recruiter_qa else None
        
        cursor.execute("""
            INSERT INTO applications (
                company_name, target_role, job_description, company_info,
                resume_text, resume_data, cover_letter, recruiter_qa, model_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company_name, target_role, job_description, company_info,
            resume_text, resume_data_json, cover_letter, recruiter_qa_json, model_used
        ))
        
        application_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        
        return application_id
    
    def get_application(self, application_id: int) -> Optional[Dict]:
        """
        Retrieve an application by ID.
        
        Args:
            application_id: The application ID
            
        Returns:
            Dict with application data, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM applications WHERE id = ?
        """, (application_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return self._row_to_dict(row)
    
    def get_all_applications(
        self, 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """
        Retrieve all applications, ordered by most recent first.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of application dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM applications ORDER BY created_at DESC"
        params = []
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params = [limit, offset]
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def search_applications(
        self,
        company_name: Optional[str] = None,
        target_role: Optional[str] = None,
        search_text: Optional[str] = None
    ) -> List[Dict]:
        """
        Search applications by company, role, or text.
        
        Args:
            company_name: Filter by company name (partial match)
            target_role: Filter by target role (partial match)
            search_text: Search in job description and company info
            
        Returns:
            List of matching application dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM applications WHERE 1=1"
        params = []
        
        if company_name:
            query += " AND company_name LIKE ?"
            params.append(f"%{company_name}%")
        
        if target_role:
            query += " AND target_role LIKE ?"
            params.append(f"%{target_role}%")
        
        if search_text:
            query += " AND (job_description LIKE ? OR company_info LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def update_application(
        self,
        application_id: int,
        **kwargs
    ) -> bool:
        """
        Update an existing application.
        
        Args:
            application_id: The application ID to update
            **kwargs: Fields to update (company_name, target_role, cover_letter, etc.)
            
        Returns:
            bool: True if updated successfully, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        allowed_fields = {
            'company_name', 'target_role', 'job_description', 'company_info',
            'resume_text', 'resume_data', 'cover_letter', 'recruiter_qa', 'model_used'
        }
        
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                # Serialize complex objects
                if field in ['resume_data', 'recruiter_qa'] and isinstance(value, (dict, list)):
                    value = json.dumps(value)
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            conn.close()
            return False
        
        # Add updated_at timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(application_id)
        
        query = f"UPDATE applications SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def delete_application(self, application_id: int) -> bool:
        """
        Delete an application by ID.
        
        Args:
            application_id: The application ID to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM applications WHERE id = ?", (application_id,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored applications.
        
        Returns:
            Dict with statistics (total count, unique companies, etc.)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        total_count = cursor.fetchone()[0]
        
        # Unique companies
        cursor.execute("SELECT COUNT(DISTINCT company_name) FROM applications WHERE company_name IS NOT NULL")
        unique_companies = cursor.fetchone()[0]
        
        # Unique roles
        cursor.execute("SELECT COUNT(DISTINCT target_role) FROM applications WHERE target_role IS NOT NULL")
        unique_roles = cursor.fetchone()[0]
        
        # Most recent application
        cursor.execute("SELECT created_at FROM applications ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        most_recent = result[0] if result else None
        
        conn.close()
        
        return {
            'total_applications': total_count,
            'unique_companies': unique_companies,
            'unique_roles': unique_roles,
            'most_recent_application': most_recent
        }
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """
        Convert a database row to a dictionary.
        
        Args:
            row: SQLite row object
            
        Returns:
            Dict with application data
        """
        data = dict(row)
        
        # Deserialize JSON fields
        if data.get('resume_data'):
            try:
                data['resume_data'] = json.loads(data['resume_data'])
            except json.JSONDecodeError:
                data['resume_data'] = {}
        
        if data.get('recruiter_qa'):
            try:
                data['recruiter_qa'] = json.loads(data['recruiter_qa'])
            except json.JSONDecodeError:
                data['recruiter_qa'] = []
        
        return data
