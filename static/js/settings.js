/**
 * Settings Page JavaScript
 * Handles settings CRUD operations, validation, and UI interactions
 */

// Global state
let currentSettings = {};
let originalSettings = {};
let currentCategory = 'ai_agent';
let hasUnsavedChanges = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page initializing...');
    
    // Load initial settings
    loadAllSettings();
    
    // Setup navigation
    setupNavigation();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Setup action buttons
    setupActionButtons();
    
    // Setup unsaved changes warning
    setupUnsavedChangesWarning();
});

/**
 * Load all settings from API
 */
async function loadAllSettings() {
    try {
        showLoading('Loading settings...');
        
        // Load current settings
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (data.success) {
            currentSettings = data.settings || {};
            originalSettings = JSON.parse(JSON.stringify(currentSettings)); // Deep copy
            
            // If settings are empty, load defaults
            if (Object.keys(currentSettings).length === 0) {
                await loadDefaults();
            } else {
                populateCurrentCategory();
            }
            
            console.log('Settings loaded:', currentSettings);
            hideLoading();
        } else {
            throw new Error(data.error || 'Failed to load settings');
        }
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showError('Failed to load settings: ' + error.message);
        hideLoading();
    }
}

/**
 * Load default settings
 */
async function loadDefaults() {
    try {
        const response = await fetch('/api/settings/defaults');
        const data = await response.json();
        
        if (data.success) {
            currentSettings = data.defaults || {};
            originalSettings = JSON.parse(JSON.stringify(currentSettings));
            populateCurrentCategory();
        }
    } catch (error) {
        console.error('Error loading defaults:', error);
    }
}

/**
 * Populate form fields for current category
 */
function populateCurrentCategory() {
    const categorySettings = currentSettings[currentCategory] || {};
    
    console.log(`Populating ${currentCategory} settings:`, categorySettings);
    
    // Populate each setting
    for (const [key, value] of Object.entries(categorySettings)) {
        const element = document.querySelector(`[name="${key}"]`);
        
        if (!element) {
            console.warn(`No input found for setting: ${key}`);
            continue;
        }
        
        // Handle different input types
        if (element.type === 'checkbox') {
            element.checked = value === true || value === 'true';
        } else if (element.type === 'radio') {
            const radio = document.querySelector(`[name="${key}"][value="${value}"]`);
            if (radio) radio.checked = true;
        } else if (element.type === 'range') {
            element.value = value;
            // Update display value
            const display = document.getElementById(element.id + '_value');
            if (display) display.textContent = value;
        } else if (key.endsWith('_days') && Array.isArray(value)) {
            // Handle checkbox arrays
            const checkboxes = document.querySelectorAll(`[name="${key}"]`);
            checkboxes.forEach(cb => {
                cb.checked = value.includes(cb.value);
            });
        } else {
            element.value = value;
        }
    }
}

/**
 * Setup navigation between categories
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.settings-nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Check for unsaved changes
            if (hasUnsavedChanges) {
                if (!confirm('You have unsaved changes. Do you want to discard them?')) {
                    return;
                }
                hasUnsavedChanges = false;
                hideUnsavedIndicator();
            }
            
            // Update active nav item
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Switch category
            const newCategory = this.dataset.category;
            switchCategory(newCategory);
        });
    });
}

/**
 * Switch to a different settings category
 */
function switchCategory(category) {
    // Hide all categories
    const categories = document.querySelectorAll('.settings-category');
    categories.forEach(cat => cat.classList.remove('active'));
    
    // Show selected category
    const selectedCategory = document.getElementById(category);
    if (selectedCategory) {
        selectedCategory.classList.add('active');
        currentCategory = category;
        populateCurrentCategory();
    }
}

/**
 * Setup form change handlers
 */
function setupFormHandlers() {
    // Handle all input changes
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            markAsChanged();
        });
        
        // Handle range slider display
        if (input.type === 'range') {
            input.addEventListener('input', function() {
                const display = document.getElementById(this.id + '_value');
                if (display) display.textContent = this.value;
            });
        }
    });
}

/**
 * Setup action button handlers
 */
function setupActionButtons() {
    // Save button
    document.getElementById('save-settings').addEventListener('click', saveSettings);
    
    // Discard button
    document.getElementById('discard-changes').addEventListener('click', discardChanges);
    
    // Reset button
    document.getElementById('reset-category').addEventListener('click', resetCategory);
}

/**
 * Save settings to API
 */
async function saveSettings() {
    try {
        showLoading('Saving settings...');
        
        // Collect current category settings from form
        const categorySettings = collectCategorySettings();
        
        // Send bulk update to API
        const response = await fetch(`/api/settings/${currentCategory}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                settings: categorySettings,
                user: 'admin', // TODO: Get from session
                reason: 'Settings page update'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update local state
            currentSettings[currentCategory] = categorySettings;
            originalSettings = JSON.parse(JSON.stringify(currentSettings));
            
            hasUnsavedChanges = false;
            hideUnsavedIndicator();
            
            showSuccess('Settings saved successfully!');
            hideLoading();
        } else {
            throw new Error(data.error || 'Failed to save settings');
        }
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings: ' + error.message);
        hideLoading();
    }
}

/**
 * Collect settings from current category form
 */
function collectCategorySettings() {
    const settings = {};
    const container = document.getElementById(currentCategory);
    
    if (!container) return settings;
    
    // Collect all inputs in the category
    const inputs = container.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        const name = input.name;
        if (!name) return;
        
        // Handle different input types
        if (input.type === 'checkbox') {
            if (name.endsWith('_days')) {
                // Handle checkbox arrays (days of week)
                if (!settings[name]) settings[name] = [];
                if (input.checked) {
                    settings[name].push(input.value);
                }
            } else {
                // Single checkbox (boolean)
                settings[name] = input.checked;
            }
        } else if (input.type === 'radio') {
            if (input.checked) {
                settings[name] = input.value;
            }
        } else if (input.type === 'number' || input.type === 'range') {
            settings[name] = parseFloat(input.value);
        } else {
            settings[name] = input.value;
        }
    });
    
    return settings;
}

/**
 * Discard unsaved changes
 */
function discardChanges() {
    if (!hasUnsavedChanges) return;
    
    if (confirm('Are you sure you want to discard your changes?')) {
        // Reload original settings
        currentSettings = JSON.parse(JSON.stringify(originalSettings));
        populateCurrentCategory();
        
        hasUnsavedChanges = false;
        hideUnsavedIndicator();
        
        showSuccess('Changes discarded');
    }
}

/**
 * Reset current category to defaults
 */
async function resetCategory() {
    if (!confirm(`Are you sure you want to reset ${currentCategory} settings to defaults? This cannot be undone.`)) {
        return;
    }
    
    try {
        showLoading('Resetting to defaults...');
        
        const response = await fetch(`/api/settings/reset/${currentCategory}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user: 'admin' // TODO: Get from session
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload settings
            await loadAllSettings();
            showSuccess('Settings reset to defaults');
        } else {
            throw new Error(data.error || 'Failed to reset settings');
        }
        
        hideLoading();
        
    } catch (error) {
        console.error('Error resetting settings:', error);
        showError('Failed to reset settings: ' + error.message);
        hideLoading();
    }
}

/**
 * Mark settings as changed
 */
function markAsChanged() {
    hasUnsavedChanges = true;
    showUnsavedIndicator();
}

/**
 * Show unsaved changes indicator
 */
function showUnsavedIndicator() {
    const indicator = document.getElementById('unsaved-indicator');
    if (indicator) indicator.classList.add('show');
}

/**
 * Hide unsaved changes indicator
 */
function hideUnsavedIndicator() {
    const indicator = document.getElementById('unsaved-indicator');
    if (indicator) indicator.classList.remove('show');
}

/**
 * Setup unsaved changes warning
 */
function setupUnsavedChangesWarning() {
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    console.log('Loading:', message);
    // TODO: Add loading overlay UI
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    console.log('Loading complete');
    // TODO: Remove loading overlay UI
}

/**
 * Show success message
 */
function showSuccess(message) {
    console.log('Success:', message);
    // TODO: Add toast notification
    alert(message); // Temporary
}

/**
 * Show error message
 */
function showError(message) {
    console.error('Error:', message);
    // TODO: Add toast notification
    alert('Error: ' + message); // Temporary
}
