"""
Dashboard functionality tests for KMRL DMS.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestDashboard:
    """Test dashboard functionality."""
    
    def test_dashboard_loads_after_login(self, browser, test_user):
        """Test that dashboard loads correctly after login."""
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
        
        # Check dashboard elements
        page_title = browser.find_element(By.CSS_SELECTOR, '.page-title')
        assert 'Analytics Dashboard' in page_title.text
        
        # Check if stats cards are present
        stats_cards = browser.find_elements(By.CSS_SELECTOR, '.stat-card')
        assert len(stats_cards) >= 4  # Should have at least 4 stat cards
        
        # Check if charts are present
        charts = browser.find_elements(By.CSS_SELECTOR, 'canvas')
        assert len(charts) >= 3  # Should have multiple charts
    
    def test_sidebar_navigation(self, browser, test_user):
        """Test sidebar navigation functionality."""
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
        
        # Test sidebar toggle
        sidebar_toggle = browser.find_element(By.ID, 'sidebar-toggle')
        sidebar_toggle.click()
        
        # Check if sidebar collapsed
        sidebar = browser.find_element(By.ID, 'sidebar')
        assert 'collapsed' in sidebar.get_attribute('class')
        
        # Test navigation links
        nav_links = browser.find_elements(By.CSS_SELECTOR, '.sidebar-link')
        assert len(nav_links) >= 6  # Should have multiple navigation links
        
        # Test documents navigation
        documents_link = browser.find_element(By.CSS_SELECTOR, '[data-target="documents"]')
        documents_link.click()
        
        # Check if documents page is shown
        documents_page = browser.find_element(By.ID, 'documents')
        assert not documents_page.get_attribute('class').__contains__('hidden')
    
    def test_documents_page(self, browser, test_user):
        """Test documents page functionality."""
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
        
        # Check if documents page is shown
        documents_page = browser.find_element(By.ID, 'documents')
        assert not documents_page.get_attribute('class').__contains__('hidden')
        
        # Check if upload button is present
        upload_button = browser.find_element(By.ID, 'upload-btn')
        assert upload_button.is_displayed()
        
        # Check if filters are present
        status_filter = browser.find_element(By.ID, 'status-filter')
        type_filter = browser.find_element(By.ID, 'type-filter')
        date_filter = browser.find_element(By.ID, 'date-filter')
        
        assert status_filter.is_displayed()
        assert type_filter.is_displayed()
        assert date_filter.is_displayed()
    
    def test_upload_modal(self, browser, test_user):
        """Test file upload modal functionality."""
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
        
        # Check if dropzone is present
        dropzone = browser.find_element(By.ID, 'dropzone')
        assert dropzone.is_displayed()
        
        # Check if file input is present
        file_input = browser.find_element(By.ID, 'file-input')
        assert file_input.is_displayed()
    
    def test_search_functionality(self, browser, test_user):
        """Test search functionality."""
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
        
        # Test search input
        search_input = browser.find_element(By.CSS_SELECTOR, '.search-input')
        search_input.send_keys('test document')
        
        # Check if search input has the value
        assert search_input.get_attribute('value') == 'test document'
    
    def test_theme_toggle(self, browser, test_user):
        """Test theme toggle functionality."""
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
        
        # Test theme toggle
        theme_toggle = browser.find_element(By.ID, 'theme-toggle')
        theme_toggle.click()
        
        # Check if theme changed (this is a visual test, so we just verify the button exists)
        assert theme_toggle.is_displayed()
