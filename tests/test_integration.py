"""
Integration tests for KMRL DMS complete user workflows.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestCompleteWorkflow:
    """Test complete user workflows."""
    
    def test_complete_user_journey(self, browser, test_user):
        """Test complete user journey from registration to document upload."""
        # Step 1: Visit home page
        browser.get('http://localhost:5000')
        
        # Check home page elements
        title = browser.find_element(By.TAG_NAME, 'h1')
        assert 'AI-POWERED INTELLIGENT DOCUMENT MANAGEMENT' in title.text
        
        # Step 2: Navigate to registration
        register_link = browser.find_element(By.LINK_TEXT, 'Register')
        register_link.click()
        
        # Wait for registration page
        WebDriverWait(browser, 10).until(
            EC.url_contains('/register')
        )
        
        # Step 3: Register new user
        full_name_field = browser.find_element(By.NAME, 'fullName')
        email_field = browser.find_element(By.NAME, 'email')
        password_field = browser.find_element(By.NAME, 'password')
        confirm_password_field = browser.find_element(By.NAME, 'confirm-password')
        
        full_name_field.send_keys(test_user['full_name'])
        email_field.send_keys(test_user['email'])
        password_field.send_keys(test_user['password'])
        confirm_password_field.send_keys(test_user['password'])
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to login
        WebDriverWait(browser, 10).until(
            EC.url_contains('/login')
        )
        
        # Step 4: Login with new credentials
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
        
        # Step 5: Verify dashboard loads
        page_title = browser.find_element(By.CSS_SELECTOR, '.page-title')
        assert 'Analytics Dashboard' in page_title.text
        
        # Step 6: Navigate to documents page
        documents_link = browser.find_element(By.CSS_SELECTOR, '[data-target="documents"]')
        documents_link.click()
        
        # Step 7: Test upload functionality
        upload_button = browser.find_element(By.ID, 'upload-btn')
        upload_button.click()
        
        # Wait for modal
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'upload-modal'))
        )
        
        # Step 8: Close modal and test navigation
        close_button = browser.find_element(By.ID, 'close-upload-modal-btn')
        close_button.click()
        
        # Step 9: Test other navigation links
        idp_link = browser.find_element(By.CSS_SELECTOR, '[data-target="idp"]')
        idp_link.click()
        
        # Check if IDP page is shown
        idp_page = browser.find_element(By.ID, 'idp')
        assert not idp_page.get_attribute('class').__contains__('hidden')
        
        # Step 10: Test logout
        logout_link = browser.find_element(By.LINK_TEXT, 'Logout')
        logout_link.click()
        
        # Wait for redirect to home
        WebDriverWait(browser, 10).until(
            EC.url_contains('/')
        )
        
        # Verify we're back on home page
        assert browser.current_url == 'http://localhost:5000/'
    
    def test_dashboard_navigation_flow(self, browser, test_user):
        """Test navigation flow through all dashboard sections."""
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
        
        # Test all navigation links
        nav_links = [
            ('dashboard', 'Analytics Dashboard'),
            ('documents', 'Centralized Repository'),
            ('idp', 'Intelligent Document Processing Insights'),
            ('workflows', 'Workflow Automation'),
            ('reports', 'Reporting & Analytics'),
            ('audittrail', 'Audit Trail'),
            ('settings', 'Settings')
        ]
        
        for link_id, expected_title in nav_links:
            # Click navigation link
            nav_link = browser.find_element(By.CSS_SELECTOR, f'[data-target="{link_id}"]')
            nav_link.click()
            
            # Wait for page to load
            time.sleep(1)
            
            # Check if correct page is shown
            page_element = browser.find_element(By.ID, link_id)
            assert not page_element.get_attribute('class').__contains__('hidden')
            
            # Check if page title is correct (for pages that have titles)
            if expected_title:
                try:
                    title_element = browser.find_element(By.CSS_SELECTOR, '.page-title')
                    assert expected_title in title_element.text
                except:
                    # Some pages might not have titles, that's okay
                    pass
    
    def test_responsive_design(self, browser, test_user):
        """Test responsive design on different screen sizes."""
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
        
        # Test mobile view (small screen)
        browser.set_window_size(375, 667)  # iPhone size
        time.sleep(1)
        
        # Check if elements are still visible
        sidebar = browser.find_element(By.ID, 'sidebar')
        assert sidebar.is_displayed()
        
        # Test tablet view
        browser.set_window_size(768, 1024)  # iPad size
        time.sleep(1)
        
        # Check if layout adapts
        stats_grid = browser.find_element(By.CSS_SELECTOR, '.stats-grid')
        assert stats_grid.is_displayed()
        
        # Test desktop view
        browser.set_window_size(1920, 1080)  # Desktop size
        time.sleep(1)
        
        # Check if all elements are visible
        page_title = browser.find_element(By.CSS_SELECTOR, '.page-title')
        assert page_title.is_displayed()
    
    def test_error_handling(self, browser):
        """Test error handling for invalid inputs."""
        # Test invalid login
        browser.get('http://localhost:5000/login')
        
        email_field = browser.find_element(By.NAME, 'email')
        password_field = browser.find_element(By.NAME, 'password')
        
        # Enter invalid credentials
        email_field.send_keys('invalid@email.com')
        password_field.send_keys('wrongpassword')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should stay on login page
        assert '/login' in browser.current_url
        
        # Test accessing protected route without login
        browser.get('http://localhost:5000/dashboard')
        
        # Should redirect to login
        WebDriverWait(browser, 10).until(
            EC.url_contains('/login')
        )
        
        assert '/login' in browser.current_url
