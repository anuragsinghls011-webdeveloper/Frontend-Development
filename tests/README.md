# KMRL DMS Test Suite

This directory contains comprehensive tests for the KMRL Document Management System.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_api.py              # API endpoint tests
├── test_auth.py             # Authentication tests
├── test_dashboard.py        # Dashboard functionality tests
├── test_file_upload.py      # File upload tests
├── test_integration.py      # Integration tests
└── README.md               # This file
```

## Test Categories

### 1. API Tests (`test_api.py`)
- Tests all API endpoints
- Verifies authentication requirements
- Checks response formats
- Tests error handling

### 2. Authentication Tests (`test_auth.py`)
- User registration flow
- User login flow
- Logout functionality
- Protected route access
- Form validation

### 3. Dashboard Tests (`test_dashboard.py`)
- Dashboard loading
- Sidebar navigation
- Statistics display
- Chart rendering
- Search functionality
- Theme toggle

### 4. File Upload Tests (`test_file_upload.py`)
- Upload modal functionality
- File selection
- Upload process
- Error handling
- Modal interactions

### 5. Integration Tests (`test_integration.py`)
- Complete user workflows
- End-to-end scenarios
- Responsive design
- Error handling
- Cross-browser compatibility

## Running Tests

### Prerequisites
Make sure your Flask application is running:
```bash
python app.py
```

### Run All Tests
```bash
python run_tests.py
```

### Run Quick Tests (API + Auth only)
```bash
python run_tests.py quick
```

### Run Specific Test Category
```bash
python run_tests.py specific test_auth.py
```

### Run Individual Test Files
```bash
pytest tests/test_auth.py -v
```

### Run with HTML Reports
```bash
pytest tests/ --html=reports/test_report.html --self-contained-html
```

## Test Configuration

The tests use the following configuration:

- **Browser**: Chrome (headless mode)
- **Test Database**: Temporary SQLite database
- **Timeout**: 10 seconds for element waits
- **Screenshots**: Automatic on test failures
- **Reports**: HTML format with screenshots

## Test Data

Tests use the following test data:

### Test User
- **Name**: Test User
- **Email**: test@kmrl.com
- **Password**: testpassword123

### Test Document
- **Type**: PDF
- **Content**: Sample PDF content
- **Size**: Small test file

## Test Reports

After running tests, check the `reports/` directory for:

- `comprehensive_test_report.html` - Complete test results
- `quick_test_report.html` - Quick test results
- Individual category reports

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - The tests automatically download ChromeDriver
   - Ensure Chrome browser is installed

2. **Flask App Not Running**
   - Make sure `python app.py` is running
   - Check that the app is accessible at `http://localhost:5000`

3. **Database Issues**
   - Tests use temporary databases
   - No cleanup required

4. **Timeout Issues**
   - Increase wait times in test files if needed
   - Check network connectivity

### Debug Mode

To run tests in debug mode:
```bash
pytest tests/ -v -s --tb=long
```

## Test Coverage

The test suite covers:

- ✅ User Authentication (Registration, Login, Logout)
- ✅ Dashboard Functionality
- ✅ File Upload System
- ✅ API Endpoints
- ✅ Navigation and UI
- ✅ Error Handling
- ✅ Responsive Design
- ✅ Integration Workflows

## Adding New Tests

To add new tests:

1. Create a new test file: `test_new_feature.py`
2. Follow the existing naming conventions
3. Use the provided fixtures from `conftest.py`
4. Add appropriate markers for test categorization
5. Update this README with new test information

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Headless browser mode
- No external dependencies
- Comprehensive error reporting
- HTML reports for easy viewing
