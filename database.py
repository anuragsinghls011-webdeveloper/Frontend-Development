import json
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_NAME = 'database.db'

def get_db_connection():
    """Database se connection banata hai."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Database tables ko initialize karta hai, agar wo exist nahi karti hain."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    
    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            uploader_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_type TEXT,
            file_size INTEGER,
            description TEXT,
            metadata TEXT,
            FOREIGN KEY (uploader_id) REFERENCES users (id)
        )
    ''')
    
    # Document Tags table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            tag_name TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Document Versions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            filename TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Workflows table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Workflow Stages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id INTEGER NOT NULL,
            stage_name TEXT NOT NULL,
            stage_order INTEGER NOT NULL,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        )
    ''')
    
    # Document Workflows table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            workflow_id INTEGER NOT NULL,
            current_stage INTEGER NOT NULL,
            assigned_to INTEGER,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id),
            FOREIGN KEY (workflow_id) REFERENCES workflows (id),
            FOREIGN KEY (current_stage) REFERENCES workflow_stages (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
    ''')
    
    # Audit Log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id INTEGER NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # IDP Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS idp_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            classification TEXT,
            extracted_data TEXT,
            confidence_score REAL,
            status TEXT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Check if a manager user exists, if not, create one
    cursor.execute("SELECT id FROM users WHERE role = 'manager'")
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (full_name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, ('Admin Manager', 'manager@kmrl.com', generate_password_hash('password', method='pbkdf2:sha256'), 'manager'))

    conn.commit()
    conn.close()
    print("Database initialized.")

# User related functions
def get_user_by_email(email):
    """Get user details by email."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user details by ID."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(full_name, email, password, role='user'):
    """Create a new user."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
            (full_name, email, password, role)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

# Document related functions
def get_user_documents(user_id):
    """Get all documents for a specific user."""
    conn = get_db_connection()
    documents = conn.execute(
        """SELECT d.*, u.full_name as uploader_name 
           FROM documents d 
           JOIN users u ON d.uploader_id = u.id 
           WHERE d.uploader_id = ? 
           ORDER BY d.upload_date DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(doc) for doc in documents]

def get_pending_documents():
    """Get all pending documents with uploader information."""
    conn = get_db_connection()
    documents = conn.execute(
        """SELECT d.*, u.full_name as uploader_name 
           FROM documents d 
           JOIN users u ON d.uploader_id = u.id 
           WHERE d.status = 'Pending' 
           ORDER BY d.upload_date DESC"""
    ).fetchall()
    conn.close()
    return [dict(doc) for doc in documents]

def create_document(filename, uploader_id, file_type=None, file_size=None, description=None):
    """Create a new document record."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO documents 
               (filename, uploader_id, file_type, file_size, description) 
               VALUES (?, ?, ?, ?, ?)""",
            (filename, uploader_id, file_type, file_size, description)
        )
        doc_id = cursor.lastrowid
        conn.commit()
        return doc_id
    finally:
        conn.close()

def update_document_status(doc_id, status):
    """Update document status."""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE documents SET status = ?, last_modified = CURRENT_TIMESTAMP WHERE id = ?",
            (status, doc_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def get_document_by_id(doc_id):
    """Get document details by ID."""
    conn = get_db_connection()
    document = conn.execute(
        """SELECT d.*, u.full_name as uploader_name 
           FROM documents d 
           JOIN users u ON d.uploader_id = u.id 
           WHERE d.id = ?""",
        (doc_id,)
    ).fetchone()
    conn.close()
    return dict(document) if document else None

# Comment related functions
def add_comment(document_id, user_id, comment_text):
    """Add a comment to a document."""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO comments (document_id, user_id, comment_text) VALUES (?, ?, ?)",
            (document_id, user_id, comment_text)
        )
        comment_id = cursor.lastrowid
        conn.commit()
        return comment_id
    finally:
        conn.close()

def get_document_comments(document_id):
    """Get all comments for a document."""
    conn = get_db_connection()
    comments = conn.execute(
        """SELECT c.*, u.full_name 
           FROM comments c 
           JOIN users u ON c.user_id = u.id 
           WHERE c.document_id = ? 
           ORDER BY c.created_at DESC""",
        (document_id,)
    ).fetchall()
    conn.close()
    return [dict(comment) for comment in comments]

# Audit log functions
def add_audit_log(user_id, action, target_type, target_id, details=None):
    """Add an entry to the audit log."""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO audit_log 
               (user_id, action, target_type, target_id, details) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, action, target_type, target_id, details)
        )
        conn.commit()
    finally:
        conn.close()

def get_recent_activity(limit=10):
    """Get recent activity from audit log."""
    conn = get_db_connection()
    activities = conn.execute(
        """SELECT a.*, u.full_name 
           FROM audit_log a 
           JOIN users u ON a.user_id = u.id 
           ORDER BY a.timestamp DESC 
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(activity) for activity in activities]

# Statistics functions
def get_user_stats(user_id):
    """Get document statistics for a user."""
    conn = get_db_connection()
    stats = {}
    
    # Total documents
    total = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE uploader_id = ?",
        (user_id,)
    ).fetchone()[0]
    stats['total_documents'] = total
    
    # Documents uploaded today
    today = conn.execute(
        """SELECT COUNT(*) FROM documents 
           WHERE uploader_id = ? 
           AND date(upload_date) = date('now')""",
        (user_id,)
    ).fetchone()[0]
    stats['uploaded_today'] = today
    
    # Pending documents
    pending = conn.execute(
        """SELECT COUNT(*) FROM documents 
           WHERE uploader_id = ? AND status = 'Pending'""",
        (user_id,)
    ).fetchone()[0]
    stats['pending_approval'] = pending
    
    # Add a mock value for archived count as the frontend expects it
    stats['archived_count'] = 0 

    conn.close()
    return stats

def create_idp_result(document_id, classification, extracted_data, status='Success', confidence=0.0):
    """Saves the result of an IDP process."""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO idp_results 
               (document_id, classification, extracted_data, confidence_score, status) 
               VALUES (?, ?, ?, ?, ?)""",
            (document_id, classification, json.dumps(extracted_data), confidence, status)
        )
        conn.commit()
    finally:
        conn.close()

def get_idp_log(limit=5):
    """Gets the most recent IDP processing logs."""
    conn = get_db_connection()
    logs = conn.execute(
        """SELECT d.filename as doc, ir.status, ir.classification as action
           FROM idp_results ir
           JOIN documents d ON ir.document_id = d.id
           ORDER BY ir.processed_at DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(log) for log in logs]
# database.py

def get_document_details(doc_id):
    """Gets all details for a single document, including IDP results."""
    conn = get_db_connection()
    
    # Get basic document info
    doc = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    if not doc:
        conn.close()
        return None
    
    doc_details = dict(doc)
    
    # Get comments
    comments = conn.execute(
        """SELECT c.*, u.full_name 
           FROM comments c JOIN users u ON c.user_id = u.id 
           WHERE c.document_id = ? ORDER BY c.created_at ASC""", (doc_id,)
    ).fetchall()
    doc_details['comments'] = [dict(c) for c in comments]
    
    # Get IDP extracted data
    idp_data = conn.execute("SELECT extracted_data FROM idp_results WHERE document_id = ?", (doc_id,)).fetchone()
    if idp_data and idp_data['extracted_data']:
        doc_details['metadata'] = json.loads(idp_data['extracted_data'])
    else:
        doc_details['metadata'] = {} # No data extracted
        
    conn.close()
    return doc_details
# database.py

def get_document_status_counts():
    """Counts documents grouped by their status."""
    conn = get_db_connection()
    counts = conn.execute(
        "SELECT status, COUNT(*) as count FROM documents GROUP BY status"
    ).fetchall()
    conn.close()
    
    # Convert the database rows into a dictionary for easier use
    return {row['status']: row['count'] for row in counts}

if __name__ == '__main__':
    init_db()
