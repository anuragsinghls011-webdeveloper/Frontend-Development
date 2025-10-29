"""
Test configuration and fixtures for KMRL DMS testing.
"""
import pytest
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app import app, init_db
import sqlite3

@pytest.fixture(scope="session")
def test_app():
    """Create a test Flask application."""
    # Create a temporary database for testing
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture(scope="function")
def browser():
    """Create a Chrome browser instance for testing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def test_user():
    """Create a test user for authentication tests."""
    return {
        'full_name': 'Test User',
        'email': 'test@kmrl.com',
        'password': 'testpassword123'
    }

@pytest.fixture(scope="function")
def test_document():
    """Create a test document for upload tests."""
    return {
        'filename': 'test_document.pdf',
        'content': b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF'
    }
