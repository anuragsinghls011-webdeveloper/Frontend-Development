document.addEventListener('DOMContentLoaded', function () {
    // Initialize theme based on user preference
    initTheme();

    // Initialize UI components and attach event listeners
    initSidebar();
    initAlerts();
    initModal();
    initBtns();
    initForms();
    initSearch();
    initUpdates();
    applyDataHighlighting();
    initPrintExport();
});

// Theme management
function initTheme() {
    const themeSwitch = document.getElementById('themeSwitch');
    const storedTheme = localStorage.getItem('mediTrackTheme');
    
    if (storedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        if (themeSwitch) themeSwitch.checked = true;
    }
    
    if (themeSwitch) {
        themeSwitch.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('mediTrackTheme', 'dark');
            } else {
                document.body.classList.remove('dark-theme');
                localStorage.setItem('mediTrackTheme', 'light');
            }
        });
    }
}

// Sidebar functionality
function initSidebar() {
    // Highlight current page in sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
    
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile sidebar toggle
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('collapsed');
        });
    }
}

// Alert dismissal functionality
function initAlerts() {
    const alertCloseButtons = document.querySelectorAll('.close-alert');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        });
    });
    
    // Auto dismiss alerts after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert) alert.style.display = 'none';
            }, 300);
        });
    }, 5000);
}

// Modal functionality
function initModal() {
    const modal = document.getElementById('modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const modalCancel = document.getElementById('modalCancel');
    
    if (!modal) return;
    
    // Close modal on X button click
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    // Close modal on Cancel button click
    if (modalCancel) {
        modalCancel.addEventListener('click', closeModal);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    // Close modal function
    function closeModal() {
        modal.classList.remove('open');
    }
    
    // Function to open modal with custom content
    window.openModal = function(title, content, confirmCallback) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').innerHTML = content;
        
        const confirmBtn = document.getElementById('modalConfirm');
        if (confirmCallback && confirmBtn) {
            confirmBtn.onclick = confirmCallback;
        }
        
        modal.classList.add('open');
    };
}

// Initialize buttons and interactive elements
function initBtns() {
    // Apply consistent button styling
    const actionButtons = document.querySelectorAll('.btn');
    actionButtons.forEach(button => {
        button.style.minWidth = '100px';
        button.style.margin = '5px 0';
    });
    
    // Initialize export buttons
    document.querySelectorAll('#exportBtn, #exportReportBtn').forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                const pageType = window.location.pathname.includes('reports') ? 'report' : 
                                 window.location.pathname.includes('medicines') ? 'medicines' :
                                 window.location.pathname.includes('equipment') ? 'equipment' :
                                 window.location.pathname.includes('general_surgery') ? 'surgery supplies' : 'data';
                
                alert(`Export functionality for ${pageType} will be available soon!`);
            });
        }
    });
    
    // Initialize print buttons
    document.querySelectorAll('#printBtn, #printReportBtn, #btnPrint').forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                window.print();
            });
        }
    });
    
    // Delete confirmation
    window.confirmDelete = function() {
        return confirm('Are you sure you want to delete this item? This action cannot be undone.');
    };
}

// Form validations and handlers
function initForms() {
    // Add form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.classList.contains('delete-form')) {
            return;  // Skip delete forms
        }
        
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Add error message if it doesn't exist
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
    
    // Add event listeners to clear error styling on input
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('error');
            const errorMsg = this.nextElementSibling;
            if (errorMsg && errorMsg.classList.contains('error-message')) {
                errorMsg.remove();
            }
        });
    });
    
    // Date field validations
    const dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        field.addEventListener('input', function() {
            if (field.id === 'next_maintenance' && document.getElementById('last_maintenance')) {
                const lastMaintenance = new Date(document.getElementById('last_maintenance').value);
                const nextMaintenance = new Date(field.value);
                
                if (nextMaintenance <= lastMaintenance) {
                    field.classList.add('error');
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        errorMsg.textContent = 'Next maintenance must be after last maintenance';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                }
            }
            
            if (field.id === 'expiry_date') {
                const today = new Date();
                const expiryDate = new Date(field.value);
                
                if (expiryDate <= today) {
                    field.classList.add('error');
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        errorMsg.textContent = 'Expiry date must be in the future';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                }
            }
        });
    });
}

// Search functionality
function initSearch() {
    const searchForm = document.querySelector('.search-global form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.classList.add('error');
                searchInput.placeholder = 'Please enter a search term';
                setTimeout(() => {
                    searchInput.classList.remove('error');
                    searchInput.placeholder = 'Search inventory...';
                }, 2000);
            }
        });
    }
}

// Update the initUpdates function in your script.js
function initUpdates() {
    const editableCells = document.querySelectorAll('td[contenteditable="true"]');
    
    editableCells.forEach(cell => {
        const row = cell.closest('tr');
        const field = cell.dataset.field;
        const type = row.dataset.type;
        
        // Initialize date picker for date fields
        if (field === 'expiry_date' || field === 'last_maintenance' || field === 'next_maintenance') {
            cell.contentEditable = false;
            const dateInput = document.createElement('input');
            dateInput.type = 'text';
            dateInput.value = cell.textContent.trim();
            dateInput.style.border = 'none';
            dateInput.style.background = 'transparent';
            dateInput.style.width = '100%';
            cell.textContent = '';
            cell.appendChild(dateInput);
            
            flatpickr(dateInput, {
                dateFormat: "Y-m-d",
                allowInput: true,
                onChange: function(selectedDates, dateStr) {
                    updateTableCell(row, field, dateStr, type);
                }
            });
        } else {
            cell.addEventListener('blur', function() {
                const newValue = this.textContent.trim();
                updateTableCell(row, field, newValue, type);
            });
        }
    });
    
    function updateTableCell(row, field, newValue, type) {
        const itemId = row.dataset.id;
        let endpoint;
        
        // Determine the endpoint based on the type
        if (type === 'general_surgery') {
            endpoint = `/update_general_surgerys/${itemId}`;
        } else if (type === 'equipment') {
            endpoint = `/update_equipments/${itemId}`;
        } else if (type === 'medicine') {
            endpoint = `/update_medicine/${itemId}`;
        } else {
            endpoint = `/update_${type}/${itemId}`;
        }
        
        // Validate date fields
        if (field.includes('date') || field.includes('maintenance')) {
            if (!isValidDate(newValue)) {
                alert('Please enter a valid date in YYYY-MM-DD format');
                return;
            }
        }
        
        // Validate numeric fields
        if (field === 'cost' || field === 'quantity') {
            if (!isValidNumber(newValue)) {
                alert('Please enter a valid number');
                return;
            }
        }
        
        const formData = new FormData();
        formData.append('field', field);
        formData.append('value', newValue);
        
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the cell with the formatted value
                const cell = row.querySelector(`td[data-field="${field}"]`);
                if (field === 'cost') {
                    cell.textContent = '₹' + parseFloat(newValue).toFixed(2);
                } else {
                    cell.textContent = newValue;
                }
            } else {
                alert('Error updating field: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating field. Please try again.');
        });
    }
    
    function isValidNumber(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    }
    
    function isValidDate(dateString) {
        const regex = /^\d{4}-\d{2}-\d{2}$/;
        if (!regex.test(dateString)) return false;
        
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }
}

// Toast notification function
window.showToast = function(message, type) {
    const toast = document.createElement('div');
    toast.classList.add('toast', `toast-${type}`);
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
};

// Function to update items in tables
window.updateItem = function(itemId, type) {
    const fieldSelect = document.getElementById(`field-${type}-${itemId}`);
    const newValueInput = document.getElementById(`newval-${type}-${itemId}`);
    
    if (!fieldSelect || !newValueInput) {
        alert('Error: Could not find form elements');
        return;
    }
    
    const field = fieldSelect.value;
    const newValue = newValueInput.value.trim();
    
    if (!newValue) {
        alert('Please enter a new value');
        return;
    }
    
    // Validate date fields
    if (field.includes('date') || field.includes('maintenance')) {
        if (!isValidDate(newValue)) {
            alert('Please enter a valid date in YYYY-MM-DD format');
            return;
        }
    }
    
    // Validate numeric fields
    if (field === 'cost' || field === 'quantity') {
        if (!isValidNumber(newValue)) {
            alert('Please enter a valid number');
            return;
        }
    }
    
    let endpoint;
    
    // Determine the endpoint based on the type
    if (type === 'general_surgery') {
        endpoint = `/update_general_surgerys/${itemId}`;
    } else if (type === 'equipment') {
        endpoint = `/update_equipments/${itemId}`;
    } else if (type === 'medicine') {
        endpoint = `/update_medicine/${itemId}`;
    } else {
        endpoint = `/update_${type}/${itemId}`;
    }
    
    const formData = new FormData();
    formData.append('field', field);
    formData.append('value', newValue);
    
    // Show loading state
    const row = document.getElementById(`row-${type}-${itemId}`);
    if (row) {
        row.classList.add('updating');
    }
    
    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the cell with the formatted value
            const cell = row.querySelector(`td:nth-child(${getColumnIndex(field, type)})`);
            if (cell) {
                if (field === 'cost') {
                    cell.textContent = '₹' + parseFloat(newValue).toFixed(2);
                } else {
                    cell.textContent = newValue;
                }
                
                // Add highlight animation
                cell.classList.add('updated');
                setTimeout(() => {
                    cell.classList.remove('updated');
                }, 2000);
            }
            
            // Clear the input
            newValueInput.value = '';
            
            // Show success message
            showToast('Item updated successfully', 'success');
        } else {
            alert('Error updating field: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating field. Please try again.');
    })
    .finally(() => {
        // Remove loading state
        if (row) {
            row.classList.remove('updating');
        }
    });
};

// Helper function to get column index based on field name
function getColumnIndex(field, type) {
    const columnMappings = {
        'equipment': {
            'name': 2,
            'manufacturer': 3,
            'cost': 4,
            'last_maintenance': 5,
            'next_maintenance': 6
        },
        'medicine': {
            'name': 2,
            'manufacturer': 3,
            'quantity': 4,
            'cost': 5,
            'expiry_date': 6
        },
        'general_surgery': {
            'name': 2,
            'manufacturer': 3,
            'cost': 4,
            'last_maintenance': 5,
            'next_maintenance': 6,
            'quantity': 7,
            'type': 8
        }
    };
    
    return columnMappings[type]?.[field] || 0;
}

// Helper function to validate numbers
function isValidNumber(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
}

// Helper function to validate dates
function isValidDate(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;
    
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date);
}

// Highlight data based on criteria
function applyDataHighlighting() {
    // Highlight expiring medicines
    document.querySelectorAll('table tr').forEach(row => {
        // Check if this is a medicine row with expiry date
        const expiryCell = row.querySelector('td:nth-child(6)');
        if (expiryCell && isValidDate(expiryCell.textContent)) {
            const expiryDate = new Date(expiryCell.textContent);
            const today = new Date();
            const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
            
            if (daysUntilExpiry <= 30 && daysUntilExpiry > 0) {
                expiryCell.classList.add('expiring-soon');
                expiryCell.setAttribute('title', `Expiring in ${daysUntilExpiry} days`);
            } 
            else if (daysUntilExpiry <= 0) {
                expiryCell.classList.add('expired');
                expiryCell.setAttribute('title', 'Expired');
            }
        }
        
        // Highlight low stock items
        const quantityCell = row.querySelector('td:nth-child(4), td:nth-child(7)');
        if (quantityCell && !isNaN(quantityCell.textContent)) {
            const quantity = parseInt(quantityCell.textContent);
            if (quantity <= 5) {
                quantityCell.classList.add('low-stock');
                quantityCell.setAttribute('title', 'Low stock');
            }
        }
        
        // Highlight equipment needing maintenance
        const nextMaintenanceCell = row.querySelector('td:nth-child(6), td:nth-child(7)');
        if (nextMaintenanceCell && isValidDate(nextMaintenanceCell.textContent)) {
            const nextMaintenance = new Date(nextMaintenanceCell.textContent);
            const today = new Date();
            const daysUntilMaintenance = Math.ceil((nextMaintenance - today) / (1000 * 60 * 60 * 24));
            
            if (daysUntilMaintenance <= 7 && daysUntilMaintenance > 0) {
                nextMaintenanceCell.classList.add('maintenance-soon');
                nextMaintenanceCell.setAttribute('title', `Maintenance due in ${daysUntilMaintenance} days`);
            } 
            else if (daysUntilMaintenance <= 0) {
                nextMaintenanceCell.classList.add('maintenance-overdue');
                nextMaintenanceCell.setAttribute('title', 'Maintenance overdue');
            }
        }
    });
    
    // Helper function to validate date
    function isValidDate(dateString) {
        if (!dateString) return false;
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }
    
    // Add CSS for highlighted cells if not already in the document
    if (!document.getElementById('highlight-styles')) {
        const style = document.createElement('style');
        style.id = 'highlight-styles';
        style.innerHTML = `
            .expiring-soon { background-color: rgba(246, 194, 62, 0.2); }
            .expired { background-color: rgba(231, 74, 59, 0.2); }
            .low-stock { background-color: rgba(231, 74, 59, 0.2); }
            .maintenance-soon { background-color: rgba(246, 194, 62, 0.2); }
            .maintenance-overdue { background-color: rgba(231, 74, 59, 0.2); }
            .updated { animation: highlight-update 2s ease; }
            
            @keyframes highlight-update {
                0% { background-color: rgba(28, 200, 138, 0.5); }
                100% { background-color: transparent; }
            }
            
            .updating { opacity: 0.6; }
            
            .toast {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 4px;
                color: white;
                opacity: 0;
                transition: all 0.3s ease;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            
            .toast-success {
                background-color: #1cc88a;
            }
            
            .toast-error {
                background-color: #e74a3b;
            }
            
            .toast.show {
                opacity: 1;
                transform: translateY(-10px);
            }
            
            .error {
                border-color: #e74a3b !important;
                box-shadow: 0 0 0 0.2rem rgba(231, 74, 59, 0.25) !important;
            }
            
            .error-message {
                color: #e74a3b;
                font-size: 0.8rem;
                margin-top: 4px;
            }
        `;
        document.head.appendChild(style);
    }
}

// Print and export functionality
function initPrintExport() {
    // Global export button
    const btnExport = document.getElementById('btnExport');
    if (btnExport) {
        btnExport.addEventListener('click', function() {
            const currentPage = window.location.pathname.split('/').pop() || 'dashboard';
            exportTableData(currentPage);
        });
    }
    
    function exportTableData(pageType) {
        // Get table data
        const table = document.querySelector('table');
        if (!table) {
            alert('No data to export');
            return;
        }
        
        // Get headers
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        
        // Get rows, excluding the action column
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {
            // Get all cells except the last one (actions)
            return Array.from(row.querySelectorAll('td:not(.action-cell)')).map(td => {
                // Replace '₹' with 'Rs.' for CSV compatibility
                const content = td.textContent.trim();
                return content.replace('₹', 'Rs.');
            });
        });
        
        // Create CSV content
        let csvContent = headers.join(',') + '\n';
        rows.forEach(row => {
            csvContent += row.join(',') + '\n';
        });
        
        // Create a download link
        const encodedUri = encodeURI('data:text/csv;charset=utf-8,' + csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `meditrack_${pageType}_export_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        
        // Trigger download
        link.click();
        
        // Clean up
        document.body.removeChild(link);
    }
}