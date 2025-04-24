/**
 * ONDC Seller App - Main JavaScript
 */

// Initialize tooltips
const initTooltips = () => {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
};

// Initialize popovers
const initPopovers = () => {
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
};

// Toggle sidebar on mobile
const initSidebar = () => {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('.main-content');
  
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      sidebar.classList.toggle('show');
    });
  }
  
  // Close sidebar when clicking outside of it on mobile
  if (mainContent && sidebar) {
    mainContent.addEventListener('click', function() {
      if (window.innerWidth < 992 && sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
      }
    });
  }
};

// Flash message auto-dismiss
const initFlashMessages = () => {
  const flashMessages = document.querySelectorAll('.alert-dismissible.auto-dismiss');
  flashMessages.forEach(function(flash) {
    setTimeout(function() {
      const closeButton = flash.querySelector('.btn-close');
      if (closeButton) {
        closeButton.click();
      }
    }, 5000);
  });
};

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2
  }).format(amount);
};

// Format date
const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('en-IN', options);
};

// Add multiple product images preview
const initImagePreview = () => {
  const imageInput = document.getElementById('images');
  const previewContainer = document.getElementById('image-preview-container');
  
  if (imageInput && previewContainer) {
    imageInput.addEventListener('change', function() {
      previewContainer.innerHTML = '';
      
      if (this.files) {
        Array.from(this.files).forEach(file => {
          if (file.type.match('image.*')) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
              const preview = document.createElement('div');
              preview.className = 'col-md-3 col-sm-4 col-6 mb-3';
              preview.innerHTML = `
                <div class="border rounded p-2 text-center">
                  <img src="${e.target.result}" class="img-fluid mb-2" alt="Preview">
                  <div class="small text-truncate">${file.name}</div>
                </div>
              `;
              previewContainer.appendChild(preview);
            };
            
            reader.readAsDataURL(file);
          }
        });
      }
    });
  }
};

// Toggle all checkboxes in a table
const initBulkCheckboxes = () => {
  const selectAll = document.getElementById('selectAll');
  
  if (selectAll) {
    selectAll.addEventListener('change', function() {
      const checkboxes = document.querySelectorAll('.item-checkbox');
      checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
      });
      
      // Toggle bulk actions button state
      const bulkActionsBtn = document.getElementById('bulkActionsBtn');
      if (bulkActionsBtn) {
        bulkActionsBtn.disabled = !document.querySelector('.item-checkbox:checked');
      }
    });
    
    // Update "Select All" checkbox when individual checkboxes change
    const checkboxes = document.querySelectorAll('.item-checkbox');
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        selectAll.checked = [...checkboxes].every(cb => cb.checked);
        selectAll.indeterminate = !selectAll.checked && [...checkboxes].some(cb => cb.checked);
        
        // Toggle bulk actions button state
        const bulkActionsBtn = document.getElementById('bulkActionsBtn');
        if (bulkActionsBtn) {
          bulkActionsBtn.disabled = !document.querySelector('.item-checkbox:checked');
        }
      });
    });
  }
};

// Date range picker initialization
const initDateRangePicker = () => {
  const dateFrom = document.getElementById('dateFrom');
  const dateTo = document.getElementById('dateTo');
  
  if (dateFrom && dateTo) {
    // Use native date inputs for simplicity
    dateFrom.addEventListener('change', function() {
      dateTo.min = this.value;
    });
    
    dateTo.addEventListener('change', function() {
      dateFrom.max = this.value;
    });
  }
};

// Product variants management
const initProductVariants = () => {
  const addVariantBtn = document.getElementById('addVariantBtn');
  const variantsContainer = document.getElementById('variantsContainer');
  
  if (addVariantBtn && variantsContainer) {
    let variantCount = document.querySelectorAll('.variant-row').length;
    
    addVariantBtn.addEventListener('click', function() {
      variantCount++;
      
      const variantRow = document.createElement('div');
      variantRow.className = 'variant-row row border rounded p-3 mb-3';
      variantRow.innerHTML = `
        <div class="col-md-12 mb-2 d-flex justify-content-between align-items-center">
          <h6 class="mb-0">Variant #${variantCount}</h6>
          <button type="button" class="btn btn-sm btn-outline-danger remove-variant">
            <i class="bi bi-trash"></i> Remove
          </button>
        </div>
        <div class="col-md-6 mb-2">
          <label class="form-label">Variant Name</label>
          <input type="text" class="form-control" name="variant_name_${variantCount}" required>
        </div>
        <div class="col-md-6 mb-2">
          <label class="form-label">SKU</label>
          <input type="text" class="form-control" name="variant_sku_${variantCount}" required>
        </div>
        <div class="col-md-6 mb-2">
          <label class="form-label">Price</label>
          <input type="number" step="0.01" class="form-control" name="variant_price_${variantCount}" required>
        </div>
        <div class="col-md-6 mb-2">
          <label class="form-label">Stock Quantity</label>
          <input type="number" class="form-control" name="variant_stock_${variantCount}" value="0">
        </div>
        <div class="col-md-12">
          <label class="form-label">Attributes (e.g. "Color: Red, Size: XL")</label>
          <input type="text" class="form-control" name="variant_attributes_${variantCount}">
        </div>
      `;
      
      variantsContainer.appendChild(variantRow);
      
      // Add event listener to the remove button
      const removeBtn = variantRow.querySelector('.remove-variant');
      removeBtn.addEventListener('click', function() {
        variantRow.remove();
      });
    });
    
    // Event delegation for removing existing variants
    variantsContainer.addEventListener('click', function(e) {
      if (e.target.closest('.remove-variant')) {
        e.target.closest('.variant-row').remove();
      }
    });
  }
};

// Order status update confirmation
// Product and Category Management
const initProductManagement = () => {
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', function(e) {
            const requiredFields = productForm.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }
};

const initImagePreview = () => {
    const imageInput = document.getElementById('images');
    const previewContainer = document.getElementById('imagePreview');
    
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            [...this.files].forEach(file => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.createElement('img');
                    preview.src = e.target.result;
                    preview.className = 'product-image-preview';
                    previewContainer.appendChild(preview);
                };
                reader.readAsDataURL(file);
            });
        });
    }
};

const initOrderStatusUpdate = () => {
  const statusButtons = document.querySelectorAll('.update-status-btn');
  
  statusButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const status = this.dataset.status;
      const orderId = this.dataset.orderId;
      const confirmMessage = `Are you sure you want to update this order to ${status}?`;
      
      if (confirm(confirmMessage)) {
        const form = document.getElementById('statusUpdateForm');
        const statusInput = document.getElementById('statusInput');
        
        statusInput.value = status;
        form.action = `/orders/${orderId}/update-status`;
        form.submit();
      }
    });
  });
};

// Notification management
const initNotifications = () => {
  const notificationBell = document.getElementById('notificationBell');
  const notificationDropdown = document.getElementById('notificationDropdown');
  const markAllReadBtn = document.getElementById('markAllReadBtn');
  
  if (notificationBell && notificationDropdown) {
    // Toggle notification dropdown manually
    notificationBell.addEventListener('click', function(e) {
      e.preventDefault();
      
      const dropdown = new bootstrap.Dropdown(notificationBell);
      dropdown.toggle();
    });
    
    // Mark individual notification as read
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
      item.addEventListener('click', function() {
        const notificationId = this.dataset.id;
        
        // Send AJAX request to mark as read
        fetch(`/api/notifications/${notificationId}/read`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.message) {
            this.classList.remove('unread');
            
            // Update notification counter
            const counter = document.getElementById('notificationCounter');
            if (counter) {
              const count = parseInt(counter.textContent) - 1;
              if (count > 0) {
                counter.textContent = count;
              } else {
                counter.style.display = 'none';
              }
            }
          }
        })
        .catch(error => console.error('Error marking notification as read:', error));
      });
    });
    
    // Mark all notifications as read
    if (markAllReadBtn) {
      markAllReadBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Send AJAX request to mark all as read
        fetch('/api/notifications/mark-all-read', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.message) {
            const unreadItems = document.querySelectorAll('.notification-item.unread');
            unreadItems.forEach(item => {
              item.classList.remove('unread');
            });
            
            // Update notification counter
            const counter = document.getElementById('notificationCounter');
            if (counter) {
              counter.style.display = 'none';
            }
          }
        })
        .catch(error => console.error('Error marking all notifications as read:', error));
      });
    }
  }
};

// Initialize all scripts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initTooltips();
  initPopovers();
  initSidebar();
  initFlashMessages();
  initImagePreview();
  initBulkCheckboxes();
  initDateRangePicker();
  initProductVariants();
  initOrderStatusUpdate();
  initNotifications();
  
  // Add other initialization functions here
});

// Make utility functions globally available
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
