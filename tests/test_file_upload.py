"""
File upload tests for KMRL DMS.
"""
import pytest
import os
import tempfile
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class TestFileUpload:
    """Test file upload functionality."""
    
    def test_file_upload_modal_opens(self, browser, test_user):
        """Test that file upload modal opens correctly."""
        # Login first
        browser.get('http://localhost:5000/login')
        
        email_field = browser.find_element(By.NAME, 'email')
        password_field = browser.find_element(By.NAME, 'password')
        
        email_field.send_keys(test_user['email'])
        password_field.send_keys(test_user['password'])
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for dashboard
        WebDriverWait(browser, 10).until(
            EC.url_contains('/dashboard')
        )
        
        # Navigate to documents page
        documents_link = browser.find_element(By.CSS_SELECTOR, '[data-target="documents"]')
        documents_link.click()
        
        # Click upload button
        upload_button = browser.find_element(By.ID, 'upload-btn')
        upload_button.click()
        
        # Check if upload modal is shown
        upload_modal = browser.find_element(By.ID, 'upload-modal')
        assert not upload_modal.get_attribute('class').__contains__('hidden')
        
        # Check modal elements
        modal_title = browser.find_element(By.CSS_SELECTOR, '.modal-title')
        assert 'Upload New Document' in modal_title.text
        
        dropzone = browser.find_element(By.ID, 'dropzone')
        assert dropzone.is_displayed()
        
        file_input = browser.find_element(By.ID, 'file-input')
        # File input might be hidden but still present in DOM
        assert file_input is not None
    
    def test_file_upload_with_text_file(self, browser, test_user):
        """Test uploading a text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('This is a test document for KMRL DMS testing.')
            temp_file_path = f.name
        
        try:
            # Login first
            browser.get('http://localhost:5000/login')
            
            email_field = browser.find_element(By.NAME, 'email')
            password_field = browser.find_element(By.NAME, 'password')
            
            email_field.send_keys(test_user['email'])
            password_field.send_keys(test_user['password'])
            
            submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            # Wait for dashboard
            WebDriverWait(browser, 10).until(
                EC.url_contains('/dashboard')
            )
            
            # Navigate to documents page
            documents_link = browser.find_element(By.CSS_SELECTOR, '[data-target="documents"]')
            documents_link.click()
            
            # Click upload button
            upload_button = browser.find_element(By.ID, 'upload-btn')
            upload_button.click()
            
            # Wait for modal to open
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'upload-modal'))
            )
            
            # Upload file
            file_input = browser.find_element(By.ID, 'file-input')
            file_input.send_keys(temp_file_path)
            
            # Wait for upload to complete (this might take a moment)
            time.sleep(2)
            
            # Check if we're redirected back to dashboard or if success message appears
            # The exact behavior depends on your implementation
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_upload_modal_close(self, browser, test_user):
        """Test that upload modal can be closed."""
        # Login first
        browser.get('http://localhost:5000/login')
        
        email_field = browser.find_element(By.NAME, 'email')
        password_field = browser.find_element(By.NAME, 'password')
        
        email_field.send_keys(test_user['email'])
        password_field.send_keys(test_user['password'])
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for dashboard
        WebDriverWait(browser, 10).until(
            EC.url_contains('/dashboard')
        )
        
        # Navigate to documents page
        documents_link = browser.find_element(By.CSS_SELECTOR, '[data-target="documents"]')
        documents_link.click()
        
        # Click upload button
        upload_button = browser.find_element(By.ID, 'upload-btn')
        upload_button.click()
        
        # Wait for modal to open
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'upload-modal'))
        )
        
        # Click close button
        close_button = browser.find_element(By.ID, 'close-upload-modal-btn')
        close_button.click()
        
        # Wait for modal to close
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'upload-modal'))
        )
        
        # Check if modal is hidden
        upload_modal = browser.find_element(By.ID, 'upload-modal')
        assert 'hidden' in upload_modal.get_attribute('class')
    
    def test_dropzone_functionality(self, browser, test_user):
        """Test dropzone drag and drop functionality."""
        # Login first
        browser.get('http://localhost:5000/login')
        
        email_field = browser.find_element(By.NAME, 'email')
        password_field = browser.find_element(By.NAME, 'password')
        
        email_field.send_keys(test_user['email'])
        password_field.send_keys(test_user['password'])
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for dashboard
        WebDriverWait(browser, 10).until(
            EC.url_contains('/dashboard')
        )
        
        # Navigate to documents page
        documents_link = browser.find_element(By.CSS_SELECTOR, '[data-target="documents"]')
        documents_link.click()
        
        # Click upload button
        upload_button = browser.find_element(By.ID, 'upload-btn')
        upload_button.click()
        
        # Wait for modal to open
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'upload-modal'))
        )
        
        # Check dropzone elements
        dropzone = browser.find_element(By.ID, 'dropzone')
        assert dropzone.is_displayed()
        
        # Check if dropzone has the correct text
        assert 'Drag & drop files here' in dropzone.text or 'browse' in dropzone.text
        
        # Test clicking on dropzone (should trigger file input)
        dropzone.click()
        
        # File input should be triggered (though we can't easily test the file dialog)
        file_input = browser.find_element(By.ID, 'file-input')
        # File input might be hidden but still present in DOM
        assert file_input is not None
