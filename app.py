from database import get_idp_log 
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import fitz
import pytesseract
from PIL import Image
import spacy
from database import get_document_status_counts

# Try to load spaCy model, but make it optional
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found. AI processing will be disabled.")
    nlp = None
from database import get_document_details
from database import (
    init_db, create_user, get_user_by_email, get_user_documents,
    create_document, update_document_status, get_pending_documents,
    get_document_by_id, add_audit_log, get_recent_activity, get_user_stats
)

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists and initialize the database
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

@app.route('/')
def home():
    """Homepage ko render karta hai."""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Naye user ke registration ko handle karta hai."""
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if user already exists
        if get_user_by_email(email):
            flash('Email address already registered.', 'error')
            return redirect(url_for('register'))

        user_id = create_user(full_name, email, hashed_password)
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            add_audit_log(user_id, 'register', 'user', user_id)
            return redirect(url_for('login'))
        else:
            flash('An error occurred during registration.', 'error')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login aur session creation ko handle karta hai."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user['role']
            add_audit_log(user['id'], 'login', 'user', user['id'])
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Session ko clear karta hai aur homepage par redirect karta hai."""
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """User ke dashboard ko unke uploaded documents ke saath display karta hai."""
    if 'user_id' not in session:
        flash('Please log in to view the dashboard.', 'info')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_name = session.get('user_name', 'Guest')
    user_role = session.get('user_role', 'user')

    # Fetch all data needed for the dashboard
    stats = get_user_stats(user_id)
    documents_raw = get_user_documents(user_id)
    recent_activity_raw = get_recent_activity(5)

    # Format documents for the frontend table
    formatted_docs = []
    for doc in documents_raw:
        formatted_docs.append({
            'id': doc['id'],
            'name': doc['filename'],
            'status': doc['status'],
            'modified': doc['upload_date'],
            'type': doc['file_type'].upper() if doc['file_type'] else 'FILE'
        })
        
    # Format recent activity for the frontend feed
    formatted_activity = []
    for activity in recent_activity_raw:
        formatted_activity.append({
            'user': activity['full_name'],
            'action': activity['action'],
            'target': activity['details'] if activity['details'] else f"{activity['target_type']} #{activity['target_id']}",
            'ts': activity['timestamp']
        })
        idp_log = get_idp_log(5)
    return render_template('dashboard.html', 
                           user_name=user_name, 
                           user_role=user_role, 
                           documents=formatted_docs,
                           stats=stats,
                           recent_activity=formatted_activity,
                           # Pass empty lists for components not yet implemented
                           idp_log=[],
                           workflows=[],
                           reports=[])

@app.route('/upload', methods=['POST'])
def upload_file():
    """User dashboard se file uploads ko handle karta hai."""
    if 'user_id' not in session:
        flash('Please log in to upload files.', 'error')
        return redirect(url_for('login'))
        
    if 'document' not in request.files:
        flash('No file part in the request.', 'error')
        return redirect(url_for('dashboard'))

    file = request.files['document']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('dashboard'))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_size = os.path.getsize(file_path)
        file_type = filename.split('.-')[-1] if '.' in filename else None

        user_id = session['user_id']
        doc_id = create_document(
            filename=filename,
            uploader_id=user_id,
            file_type=file_type,     
            file_size=file_size
        )
        process_document_with_ai(file_path, doc_id)

        add_audit_log(
            user_id=user_id,
            action='upload',
            target_type='document',
            target_id=doc_id,
            details=f'Uploaded file: {filename}'
        )

        flash(f'File "{filename}" uploaded successfully! It is now pending approval.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin_dashboard():
    """Document management ke liye admin panel display karta hai."""
    if session.get('user_role') != 'manager':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

    pending_docs_raw = get_pending_documents()
    
    formatted_docs = []
    for doc in pending_docs_raw:
        doc_dict = dict(doc)
        doc_dict['full_name'] = doc_dict.pop('uploader_name', 'Unknown Uploader')
        
        # --- YEH HAI FIX ---
        # Database se aaye date string ko Python ke datetime object mein badalna
        if doc_dict.get('upload_date'):
            try:
                # Format ko database ke timestamp format se match karna
                doc_dict['upload_date'] = datetime.strptime(doc_dict['upload_date'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                # Agar conversion fail ho, to use None set kar dena
                doc_dict['upload_date'] = None
        # --- FIX END ---
        
        formatted_docs.append(doc_dict)
        
    return render_template('admin.html', documents=formatted_docs)
@app.route('/approve/<int:doc_id>')
def approve_document(doc_id):
    """Pending document ko approve karta hai."""
    if session.get('user_role') != 'manager':
        return redirect(url_for('dashboard'))

    doc = get_document_by_id(doc_id)
    if doc:
        update_document_status(doc_id, 'Approved')
        add_audit_log(
            user_id=session['user_id'],
            action='approve',
            target_type='document',
            target_id=doc_id,
            details=f"Approved '{doc['filename']}'"
        )
        flash('Document has been approved.', 'success')
    else:
        flash('Error approving document.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject/<int:doc_id>')
def reject_document(doc_id):
    """Pending document ko reject karta hai."""
    if session.get('user_role') != 'manager':
        return redirect(url_for('dashboard'))

    doc = get_document_by_id(doc_id)
    if doc:
        update_document_status(doc_id, 'Rejected')
        add_audit_log(
            user_id=session['user_id'],
            action='reject',
            target_type='document',
            target_id=doc_id,
            details=f"Rejected '{doc['filename']}'"
        )
        flash('Document has been rejected.', 'success')
    else:
        flash('Error rejecting document.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/dashboard')
def api_dashboard_data():
    """Provides dashboard data as JSON for dynamic frontend updates."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    documents_raw = get_user_documents(user_id)
    stats = get_user_stats(user_id)
    recent_activity_raw = get_recent_activity(5)

    # Format documents
    formatted_docs = []
    for doc in documents_raw:
        formatted_docs.append({
            'id': doc['id'],
            'name': doc['filename'],
            'status': doc['status'],
            'modified': doc['upload_date'],
            'type': doc['file_type'].upper() if doc['file_type'] else 'FILE'
        })
    
    # Format recent activity
    formatted_activity = []
    for activity in recent_activity_raw:
        formatted_activity.append({
            'user': activity['full_name'],
            'action': activity['action'],
            'target': activity['details'] if activity['details'] else f"{activity['target_type']} #{activity['target_id']}",
            'ts': activity['timestamp']
        })

    return jsonify({
        'stats': stats,
        'documents': formatted_docs,
        'recent_activity': formatted_activity,
        'idp_log': []  # Mock data for now
    })

@app.route('/api/charts/document_status')
def api_document_status_chart():
    """Provides document status data for charts."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    
    user_id = session['user_id']
    status_counts = get_document_status_counts(user_id)
    
    # Format data for Chart.js
    labels = []
    data = []
    colors = ['#22c55e', '#facc15', '#3b82f6', '#6b7280', '#ef4444']
    
    for status, count in status_counts.items():
        labels.append(status)
        data.append(count)
    
    return jsonify({
        'labels': labels,
        'data': data,
        'colors': colors[:len(labels)]
    })

@app.route('/api/document/<int:doc_id>')
def api_document_details(doc_id):
    """Get detailed information about a specific document."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    doc_details = get_document_details(doc_id, user_id)
    
    if not doc_details:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(doc_details)

@app.route('/api/search')
def api_search():
    """Search documents by filename, content, or tags."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    query = request.args.get('q', '')
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    date_filter = request.args.get('date', '')
    
    # Get all user documents
    documents_raw = get_user_documents(user_id)
    
    # Apply filters
    filtered_docs = []
    for doc in documents_raw:
        # Text search
        if query and query.lower() not in doc['filename'].lower():
            continue
            
        # Status filter
        if status_filter != 'all' and doc['status'] != status_filter:
            continue
            
        # Type filter
        if type_filter != 'all' and doc['file_type'] != type_filter.lower():
            continue
            
        # Date filter (simplified)
        if date_filter:
            doc_date = doc['upload_date'].split(' ')[0] if ' ' in doc['upload_date'] else doc['upload_date']
            if doc_date != date_filter:
                continue
        
        filtered_docs.append({
            'id': doc['id'],
            'name': doc['filename'],
            'status': doc['status'],
            'modified': doc['upload_date'],
            'type': doc['file_type'].upper() if doc['file_type'] else 'FILE'
        })
    
    return jsonify({'documents': filtered_docs})

@app.route('/api/update_document/<int:doc_id>', methods=['POST'])
def api_update_document(doc_id):
    """Update document metadata."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    # Verify document belongs to user
    doc = get_document_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({'error': 'Document not found'}), 404
    
    # Update document (you'll need to implement this in database.py)
    # For now, just return success
    return jsonify({'success': True, 'message': 'Document updated successfully'})

@app.route('/api/delete_document/<int:doc_id>', methods=['DELETE'])
def api_delete_document(doc_id):
    """Delete a document."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    # Verify document belongs to user
    doc = get_document_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({'error': 'Document not found'}), 404
    
    # Delete document (you'll need to implement this in database.py)
    # For now, just return success
    return jsonify({'success': True, 'message': 'Document deleted successfully'})
# app.py

def process_document_with_ai(file_path, doc_id):
    """Extracts text and entities from a document and saves the results."""
    text = ""
    file_type = file_path.split('.')[-1].lower()

    try:
        # 1. Extract Text (OCR for images, text extraction for PDF)
        if file_type == 'pdf':
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif file_type in ['png', 'jpg', 'jpeg', 'tiff']:
            text = pytesseract.image_to_string(Image.open(file_path))

        if not text:
            return # Skip if no text could be extracted

        # 2. Extract Entities using spaCy (if available)
        entities = {}
        if nlp:
            doc_nlp = nlp(text)
            for ent in doc_nlp.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
        
        # Make entity lists unique
        for label, items in entities.items():
            entities[label] = list(set(items))

        # 3. Save to Database
        # (This is a simple classification, you can make it smarter)
        classification = "Invoice" if "invoice" in text.lower() else "General Document"
        
        # Import the function from your database file
        from database import create_idp_result
        create_idp_result(doc_id, classification, entities, status='Success')
        print(f"IDP Processing successful for doc_id: {doc_id}")

    except Exception as e:
        print(f"Error during AI processing for {file_path}: {e}")
        from database import create_idp_result
        create_idp_result(doc_id, "Unknown", {}, status='Failed')
# app.py

@app.route('/api/charts/document_status')
def chart_document_status():
    """Provides data for the document status pie chart."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    status_counts = get_document_status_counts()

    labels = list(status_counts.keys())
    data = list(status_counts.values())

    # --- YEH HAI FIX ---
    # Ek JSON response banayein aur usmein caching ko disable karne ke liye headers add karein
    response_data = jsonify({
        'labels': labels,
        'data': data
    })

    response = make_response(response_data)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response
    # --- FIX END ---
   

if __name__ == '__main__':
    app.run(debug=True)