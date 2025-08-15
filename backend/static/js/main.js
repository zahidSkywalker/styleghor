/**
 * Main JavaScript file for Style Ghor E-commerce Platform
 * Handles cart operations, AJAX requests, and interactive features
 */

// Global variables
let cartCount = 0;
let isProcessing = false;

// Initialize when document is ready
$(document).ready(function() {
    initializeApp();
    setupEventListeners();
    loadCartCount();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Add CSRF token to all AJAX requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
            }
        }
    });
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize animations
    initializeAnimations();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Add to cart buttons
    $(document).on('click', '.add-to-cart', function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        const quantity = $(this).closest('.product-card').find('.quantity-input').val() || 1;
        const variantId = $(this).closest('.product-card').find('input[name^="variant_"]:checked').val();
        
        addToCart(productId, quantity, variantId);
    });
    
    // Add to wishlist buttons
    $(document).on('click', '.add-to-wishlist', function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        addToWishlist(productId);
    });
    
    // Quantity change events
    $(document).on('change', '.quantity-input', function() {
        const productId = $(this).closest('.product-card').data('product-id');
        const quantity = $(this).val();
        updateProductQuantity(productId, quantity);
    });
    
    // Search functionality
    $('#searchForm').on('submit', function(e) {
        e.preventDefault();
        performSearch();
    });
    
    // Newsletter subscription
    $('#newsletterForm').on('submit', function(e) {
        e.preventDefault();
        subscribeNewsletter();
    });
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all product cards and sections
    document.querySelectorAll('.product-card, .card, .hero-section').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Add product to cart
 */
function addToCart(productId, quantity = 1, variantId = null) {
    if (isProcessing) return;
    
    isProcessing = true;
    showLoadingState();
    
    const data = {
        product_id: productId,
        quantity: quantity
    };
    
    if (variantId) {
        data.variant_id = variantId;
    }
    
    $.ajax({
        url: '/cart/add/',
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            if (response.status === 'success') {
                updateCartCount(response.cart_count);
                showAlert('Product added to cart successfully!', 'success');
                
                // Update cart icon animation
                animateCartIcon();
                
                // Update any quantity displays
                updateQuantityDisplays(productId, quantity);
            } else {
                showAlert(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error adding to cart:', error);
            showAlert('Error adding product to cart. Please try again.', 'error');
        },
        complete: function() {
            isProcessing = false;
            hideLoadingState();
        }
    });
}

/**
 * Add product to wishlist
 */
function addToWishlist(productId) {
    if (isProcessing) return;
    
    isProcessing = true;
    showLoadingState();
    
    $.ajax({
        url: `/wishlist/add/${productId}/`,
        method: 'POST',
        success: function(response) {
            if (response.status === 'success') {
                showAlert('Product added to wishlist!', 'success');
                
                // Update wishlist button
                const button = $(`.add-to-wishlist[data-product-id="${productId}"]`);
                button.removeClass('btn-outline-secondary').addClass('btn-success');
                button.html('<i class="fas fa-heart"></i> Added');
                
                setTimeout(() => {
                    button.removeClass('btn-success').addClass('btn-outline-secondary');
                    button.html('<i class="fas fa-heart"></i>');
                }, 2000);
            } else {
                showAlert(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error adding to wishlist:', error);
            showAlert('Error adding product to wishlist. Please try again.', 'error');
        },
        complete: function() {
            isProcessing = false;
            hideLoadingState();
        }
    });
}

/**
 * Update product quantity
 */
function updateProductQuantity(productId, quantity) {
    if (quantity < 1) return;
    
    const data = { quantity: quantity };
    
    $.ajax({
        url: `/cart/update/${productId}/`,
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            if (response.status === 'success') {
                updateCartCount(response.cart_count);
                updateProductTotal(productId, response.item_total);
                updateCartTotal(response.cart_total);
                showAlert('Quantity updated successfully!', 'success');
            } else {
                showAlert(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error updating quantity:', error);
            showAlert('Error updating quantity. Please try again.', 'error');
        }
    });
}

/**
 * Remove product from cart
 */
function removeFromCart(productId) {
    if (!confirm('Are you sure you want to remove this item from your cart?')) {
        return;
    }
    
    $.ajax({
        url: `/cart/remove/${productId}/`,
        method: 'POST',
        success: function(response) {
            if (response.status === 'success') {
                updateCartCount(response.cart_count);
                removeProductFromDisplay(productId);
                updateCartTotal(response.cart_total);
                showAlert('Product removed from cart', 'success');
                
                // Check if cart is empty
                if (response.cart_count === 0) {
                    showEmptyCartMessage();
                }
            } else {
                showAlert(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error removing from cart:', error);
            showAlert('Error removing product. Please try again.', 'error');
        }
    });
}

/**
 * Load cart count from server
 */
function loadCartCount() {
    $.ajax({
        url: '/cart/count/',
        method: 'GET',
        success: function(response) {
            if (response.cart_count !== undefined) {
                updateCartCount(response.cart_count);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading cart count:', error);
        }
    });
}

/**
 * Update cart count display
 */
function updateCartCount(count) {
    cartCount = count;
    $('.cart-count').text(count);
    
    // Animate cart count change
    $('.cart-count').addClass('animate__animated animate__pulse');
    setTimeout(() => {
        $('.cart-count').removeClass('animate__animated animate__pulse');
    }, 1000);
}

/**
 * Update product total in cart
 */
function updateProductTotal(productId, total) {
    $(`.cart-item[data-product-id="${productId}"] .product-total`).text(`৳${total}`);
}

/**
 * Update cart total
 */
function updateCartTotal(total) {
    $('.cart-total').text(`৳${total}`);
}

/**
 * Remove product from display
 */
function removeProductFromDisplay(productId) {
    $(`.cart-item[data-product-id="${productId}"]`).fadeOut(300, function() {
        $(this).remove();
    });
}

/**
 * Show empty cart message
 */
function showEmptyCartMessage() {
    $('.cart-items').html(`
        <div class="text-center py-4">
            <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
            <h5>Your cart is empty</h5>
            <p class="text-muted">Add some products to get started!</p>
        </div>
    `);
}

/**
 * Perform search
 */
function performSearch() {
    const query = $('#searchInput').val().trim();
    if (!query) return;
    
    // Show loading state
    $('#searchResults').html('<div class="text-center py-4"><i class="fas fa-spinner fa-spin fa-2x"></i></div>');
    
    $.ajax({
        url: '/search/',
        method: 'GET',
        data: { q: query },
        success: function(response) {
            displaySearchResults(response.results, query);
        },
        error: function(xhr, status, error) {
            console.error('Search error:', error);
            $('#searchResults').html('<div class="alert alert-danger">Error performing search. Please try again.</div>');
        }
    });
}

/**
 * Display search results
 */
function displaySearchResults(results, query) {
    if (results.length === 0) {
        $('#searchResults').html(`
            <div class="text-center py-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No results found</h5>
                <p class="text-muted">Try different keywords or browse our categories.</p>
            </div>
        `);
        return;
    }
    
    let html = `<h5>Search results for "${query}" (${results.length} found)</h5><div class="row g-3">`;
    
    results.forEach(product => {
        html += `
            <div class="col-md-6 col-lg-4">
                <div class="card product-card">
                    <div class="card-body">
                        <h6 class="card-title">${product.name}</h6>
                        <p class="card-text text-muted">${product.short_description}</p>
                        <p class="fw-bold">৳${product.current_price}</p>
                        <button class="btn btn-primary btn-sm add-to-cart" data-product-id="${product.id}">
                            Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    $('#searchResults').html(html);
}

/**
 * Subscribe to newsletter
 */
function subscribeNewsletter() {
    const email = $('#newsletterEmail').val().trim();
    if (!email) {
        showAlert('Please enter your email address', 'warning');
        return;
    }
    
    $.ajax({
        url: '/newsletter/subscribe/',
        method: 'POST',
        data: { email: email },
        success: function(response) {
            if (response.status === 'success') {
                showAlert('Successfully subscribed to newsletter!', 'success');
                $('#newsletterEmail').val('');
            } else {
                showAlert(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('Newsletter subscription error:', error);
            showAlert('Error subscribing to newsletter. Please try again.', 'error');
        }
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const iconClass = getAlertIcon(type);
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="${iconClass} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Remove existing alerts
    $('.alert').remove();
    
    // Add new alert
    $('body').prepend(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        $('.alert').fadeOut(300, function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Get alert icon based on type
 */
function getAlertIcon(type) {
    switch (type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    $('body').addClass('loading');
    $('.btn:disabled').prop('disabled', true);
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    $('body').removeClass('loading');
    $('.btn:disabled').prop('disabled', false);
}

/**
 * Animate cart icon
 */
function animateCartIcon() {
    $('.cart-icon').addClass('animate__animated animate__bounce');
    setTimeout(() => {
        $('.cart-icon').removeClass('animate__animated animate__bounce');
    }, 1000);
}

/**
 * Update quantity displays
 */
function updateQuantityDisplays(productId, quantity) {
    $(`.product-card[data-product-id="${productId}"] .quantity-input`).val(quantity);
}

/**
 * Get CSRF token
 */
function getCSRFToken() {
    return $('[name=csrfmiddlewaretoken]').val() || $('meta[name=csrf-token]').attr('content');
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-BD', {
        style: 'currency',
        currency: 'BDT',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number format
 */
function isValidPhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for scroll events
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for use in other scripts
window.StyleGhor = {
    addToCart,
    addToWishlist,
    removeFromCart,
    updateProductQuantity,
    showAlert,
    formatCurrency,
    isValidEmail,
    isValidPhone
};

// Add to global scope for backward compatibility
window.addToCart = addToCart;
window.addToWishlist = addToWishlist;
window.removeFromCart = removeFromCart;
window.showAlert = showAlert;