"""
API endpoint tests for KMRL DMS.
"""
import pytest
import json

class TestAPIEndpoints:
    """Test API endpoints functionality."""
    
    def test_dashboard_api_unauthorized(self, test_app):
        """Test that dashboard API requires authentication."""
        response = test_app.get('/api/dashboard')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not logged in'
    
    def test_document_status_chart_api_unauthorized(self, test_app):
        """Test that document status chart API requires authentication."""
        response = test_app.get('/api/charts/document_status')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not authorized'
    
    def test_document_details_api_unauthorized(self, test_app):
        """Test that document details API requires authentication."""
        response = test_app.get('/api/document/1')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not logged in'
    
    def test_upload_endpoint_unauthorized(self, test_app):
        """Test that upload endpoint requires authentication."""
        response = test_app.post('/upload')
        assert response.status_code == 302  # Redirects to login
    
    def test_admin_endpoint_unauthorized(self, test_app):
        """Test that admin endpoint requires authentication."""
        response = test_app.get('/admin')
        assert response.status_code == 302  # Redirects to dashboard
    
    def test_approve_document_unauthorized(self, test_app):
        """Test that approve document endpoint requires authentication."""
        response = test_app.get('/approve/1')
        assert response.status_code == 302  # Redirects to dashboard
    
    def test_reject_document_unauthorized(self, test_app):
        """Test that reject document endpoint requires authentication."""
        response = test_app.get('/reject/1')
        assert response.status_code == 302  # Redirects to dashboard
