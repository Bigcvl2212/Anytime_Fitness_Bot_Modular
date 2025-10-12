/**
 * Admin Settings JavaScript Controller
 * Manages admin system configuration including security, permissions, logging, backups, API, webhooks
 */

let adminSettings = {};
let originalSettings = {};
let hasUnsavedChanges = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initializing admin settings...');
    
    loadAdminSettings();
    setupNavigation();
    setupChangeTracking();
    setupBeforeUnload();
});

/**
 * Load admin settings from API
 */
async function loadAdminSettings() {
    try {
        const response = await fetch('/api/settings/admin');
        
        if (!response.ok) {
            console.warn('Admin settings API not yet implemented, using defaults');
            adminSettings = getDefaultAdminSettings();
        } else {
            const data = await response.json();
            adminSettings = data.settings || getDefaultAdminSettings();
        }
        
        originalSettings = JSON.parse(JSON.stringify(adminSettings));
        populateAllSections();
        
        console.log('✅ Admin settings loaded successfully');
        
    } catch (error) {
        console.error('Error loading admin settings:', error);
        adminSettings = getDefaultAdminSettings();
        originalSettings = JSON.parse(JSON.stringify(adminSettings));
        populateAllSections();
    }
}

/**
 * Get default admin settings structure
 */
function getDefaultAdminSettings() {
    return {
        security: {
            session_timeout: 30,
            max_login_attempts: 5,
            lockout_duration: 15,
            require_password_change: true,
            enable_2fa: false,
            allowed_ips: ''
        },
        permissions: {
            default_perms: ['dashboard_view'],
            allow_permission_escalation: false,
            require_approval_for_super_admin: true
        },
        authentication: {
            password_min_length: 8,
            password_require_uppercase: true,
            password_require_lowercase: true,
            password_require_numbers: true,
            password_require_special: false,
            password_history: 5,
            auth_method: 'database'
        },
        maintenance: {
            maintenance_mode: false,
            maintenance_message: 'System is undergoing scheduled maintenance. Please check back soon.',
            auto_restart: 'enabled',
            auto_vacuum: true,
            auto_optimize: true
        },
        logging: {
            log_level: 'INFO',
            log_retention_days: 90,
            audit_login_attempts: true,
            audit_permission_changes: true,
            audit_data_access: true,
            audit_api_calls: false,
            audit_retention_days: 365
        },
        backups: {
            auto_backup_enabled: true,
            backup_frequency: 'daily',
            backup_time: '02:00',
            backup_retention_count: 7,
            backup_location: './backups',
            backup_compress: true
        },
        api: {
            api_enabled: true,
            api_rate_limit: 60,
            api_key_expiration: 90,
            api_require_auth: true,
            cors_origins: ''
        },
        webhooks: {
            webhooks_enabled: false,
            webhook_system_errors: '',
            webhook_admin_actions: '',
            webhook_data_changes: '',
            webhook_retry_attempts: 3,
            webhook_timeout: 30
        }
    };
}

/**
 * Populate all form sections with current settings
 */
function populateAllSections() {
    // Security section
    setInputValue('session_timeout', adminSettings.security?.session_timeout);
    setInputValue('max_login_attempts', adminSettings.security?.max_login_attempts);
    setInputValue('lockout_duration', adminSettings.security?.lockout_duration);
    setCheckboxValue('require_password_change', adminSettings.security?.require_password_change);
    setCheckboxValue('enable_2fa', adminSettings.security?.enable_2fa);
    setInputValue('allowed_ips', adminSettings.security?.allowed_ips);
    
    // Permissions section
    const defaultPerms = adminSettings.permissions?.default_perms || [];
    document.querySelectorAll('input[name="default_perms"]').forEach(checkbox => {
        checkbox.checked = defaultPerms.includes(checkbox.value);
    });
    setCheckboxValue('allow_permission_escalation', adminSettings.permissions?.allow_permission_escalation);
    setCheckboxValue('require_approval_for_super_admin', adminSettings.permissions?.require_approval_for_super_admin);
    
    // Authentication section
    setInputValue('password_min_length', adminSettings.authentication?.password_min_length);
    setCheckboxValue('password_require_uppercase', adminSettings.authentication?.password_require_uppercase);
    setCheckboxValue('password_require_lowercase', adminSettings.authentication?.password_require_lowercase);
    setCheckboxValue('password_require_numbers', adminSettings.authentication?.password_require_numbers);
    setCheckboxValue('password_require_special', adminSettings.authentication?.password_require_special);
    setInputValue('password_history', adminSettings.authentication?.password_history);
    setInputValue('auth_method', adminSettings.authentication?.auth_method);
    
    // Maintenance section
    setCheckboxValue('maintenance_mode', adminSettings.maintenance?.maintenance_mode);
    setInputValue('maintenance_message', adminSettings.maintenance?.maintenance_message);
    setInputValue('auto_restart', adminSettings.maintenance?.auto_restart);
    setCheckboxValue('auto_vacuum', adminSettings.maintenance?.auto_vacuum);
    setCheckboxValue('auto_optimize', adminSettings.maintenance?.auto_optimize);
    
    // Logging section
    setInputValue('log_level', adminSettings.logging?.log_level);
    setInputValue('log_retention_days', adminSettings.logging?.log_retention_days);
    setCheckboxValue('audit_login_attempts', adminSettings.logging?.audit_login_attempts);
    setCheckboxValue('audit_permission_changes', adminSettings.logging?.audit_permission_changes);
    setCheckboxValue('audit_data_access', adminSettings.logging?.audit_data_access);
    setCheckboxValue('audit_api_calls', adminSettings.logging?.audit_api_calls);
    setInputValue('audit_retention_days', adminSettings.logging?.audit_retention_days);
    
    // Backups section
    setCheckboxValue('auto_backup_enabled', adminSettings.backups?.auto_backup_enabled);
    setInputValue('backup_frequency', adminSettings.backups?.backup_frequency);
    setInputValue('backup_time', adminSettings.backups?.backup_time);
    setInputValue('backup_retention_count', adminSettings.backups?.backup_retention_count);
    setInputValue('backup_location', adminSettings.backups?.backup_location);
    setCheckboxValue('backup_compress', adminSettings.backups?.backup_compress);
    
    // API section
    setCheckboxValue('api_enabled', adminSettings.api?.api_enabled);
    setInputValue('api_rate_limit', adminSettings.api?.api_rate_limit);
    setInputValue('api_key_expiration', adminSettings.api?.api_key_expiration);
    setCheckboxValue('api_require_auth', adminSettings.api?.api_require_auth);
    setInputValue('cors_origins', adminSettings.api?.cors_origins);
    
    // Webhooks section
    setCheckboxValue('webhooks_enabled', adminSettings.webhooks?.webhooks_enabled);
    setInputValue('webhook_system_errors', adminSettings.webhooks?.webhook_system_errors);
    setInputValue('webhook_admin_actions', adminSettings.webhooks?.webhook_admin_actions);
    setInputValue('webhook_data_changes', adminSettings.webhooks?.webhook_data_changes);
    setInputValue('webhook_retry_attempts', adminSettings.webhooks?.webhook_retry_attempts);
    setInputValue('webhook_timeout', adminSettings.webhooks?.webhook_timeout);
}

/**
 * Helper to set input value safely
 */
function setInputValue(id, value) {
    const element = document.getElementById(id);
    if (element && value !== undefined && value !== null) {
        element.value = value;
    }
}

/**
 * Helper to set checkbox value safely
 */
function setCheckboxValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.checked = !!value;
    }
}

/**
 * Setup section navigation
 */
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check for unsaved changes
            if (hasUnsavedChanges) {
                if (!confirm('You have unsaved changes. Switch sections anyway?')) {
                    return;
                }
            }
            
            const sectionId = this.dataset.section;
            
            // Update nav active state
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            // Show target section
            document.querySelectorAll('.settings-section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
        });
    });
}

/**
 * Track changes for unsaved indicator
 */
function setupChangeTracking() {
    const form = document.querySelector('.settings-content');
    
    form.addEventListener('input', function() {
        hasUnsavedChanges = true;
        document.getElementById('unsaved-indicator').style.display = 'block';
    });
    
    form.addEventListener('change', function() {
        hasUnsavedChanges = true;
        document.getElementById('unsaved-indicator').style.display = 'block';
    });
}

/**
 * Warn before leaving with unsaved changes
 */
function setupBeforeUnload() {
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });
}

/**
 * Collect all settings from forms
 */
function collectAllSettings() {
    const collected = {
        security: {
            session_timeout: parseInt(document.getElementById('session_timeout').value),
            max_login_attempts: parseInt(document.getElementById('max_login_attempts').value),
            lockout_duration: parseInt(document.getElementById('lockout_duration').value),
            require_password_change: document.getElementById('require_password_change').checked,
            enable_2fa: document.getElementById('enable_2fa').checked,
            allowed_ips: document.getElementById('allowed_ips').value.trim()
        },
        permissions: {
            default_perms: Array.from(document.querySelectorAll('input[name="default_perms"]:checked'))
                .map(cb => cb.value),
            allow_permission_escalation: document.getElementById('allow_permission_escalation').checked,
            require_approval_for_super_admin: document.getElementById('require_approval_for_super_admin').checked
        },
        authentication: {
            password_min_length: parseInt(document.getElementById('password_min_length').value),
            password_require_uppercase: document.getElementById('password_require_uppercase').checked,
            password_require_lowercase: document.getElementById('password_require_lowercase').checked,
            password_require_numbers: document.getElementById('password_require_numbers').checked,
            password_require_special: document.getElementById('password_require_special').checked,
            password_history: parseInt(document.getElementById('password_history').value),
            auth_method: document.getElementById('auth_method').value
        },
        maintenance: {
            maintenance_mode: document.getElementById('maintenance_mode').checked,
            maintenance_message: document.getElementById('maintenance_message').value,
            auto_restart: document.getElementById('auto_restart').value,
            auto_vacuum: document.getElementById('auto_vacuum').checked,
            auto_optimize: document.getElementById('auto_optimize').checked
        },
        logging: {
            log_level: document.getElementById('log_level').value,
            log_retention_days: parseInt(document.getElementById('log_retention_days').value),
            audit_login_attempts: document.getElementById('audit_login_attempts').checked,
            audit_permission_changes: document.getElementById('audit_permission_changes').checked,
            audit_data_access: document.getElementById('audit_data_access').checked,
            audit_api_calls: document.getElementById('audit_api_calls').checked,
            audit_retention_days: parseInt(document.getElementById('audit_retention_days').value)
        },
        backups: {
            auto_backup_enabled: document.getElementById('auto_backup_enabled').checked,
            backup_frequency: document.getElementById('backup_frequency').value,
            backup_time: document.getElementById('backup_time').value,
            backup_retention_count: parseInt(document.getElementById('backup_retention_count').value),
            backup_location: document.getElementById('backup_location').value,
            backup_compress: document.getElementById('backup_compress').checked
        },
        api: {
            api_enabled: document.getElementById('api_enabled').checked,
            api_rate_limit: parseInt(document.getElementById('api_rate_limit').value),
            api_key_expiration: parseInt(document.getElementById('api_key_expiration').value),
            api_require_auth: document.getElementById('api_require_auth').checked,
            cors_origins: document.getElementById('cors_origins').value.trim()
        },
        webhooks: {
            webhooks_enabled: document.getElementById('webhooks_enabled').checked,
            webhook_system_errors: document.getElementById('webhook_system_errors').value.trim(),
            webhook_admin_actions: document.getElementById('webhook_admin_actions').value.trim(),
            webhook_data_changes: document.getElementById('webhook_data_changes').value.trim(),
            webhook_retry_attempts: parseInt(document.getElementById('webhook_retry_attempts').value),
            webhook_timeout: parseInt(document.getElementById('webhook_timeout').value)
        }
    };
    
    return collected;
}

/**
 * Save all admin settings
 */
async function saveAdminSettings() {
    try {
        const settingsToSave = collectAllSettings();
        
        console.log('💾 Saving admin settings...', settingsToSave);
        
        const response = await fetch('/api/settings/admin', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                settings: settingsToSave,
                updated_by: 'current_admin',  // TODO: Get from session
                reason: 'Admin settings update'
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save settings');
        }
        
        const data = await response.json();
        
        // Update local state
        adminSettings = settingsToSave;
        originalSettings = JSON.parse(JSON.stringify(adminSettings));
        hasUnsavedChanges = false;
        document.getElementById('unsaved-indicator').style.display = 'none';
        
        alert('✅ Admin settings saved successfully!');
        console.log('✅ Settings saved:', data);
        
    } catch (error) {
        console.error('❌ Error saving admin settings:', error);
        alert(`Failed to save settings: ${error.message}`);
    }
}

/**
 * Discard changes and reload original settings
 */
function discardAdminChanges() {
    if (!hasUnsavedChanges) {
        alert('No unsaved changes to discard');
        return;
    }
    
    if (!confirm('Discard all unsaved changes?')) {
        return;
    }
    
    adminSettings = JSON.parse(JSON.stringify(originalSettings));
    populateAllSections();
    hasUnsavedChanges = false;
    document.getElementById('unsaved-indicator').style.display = 'none';
    
    console.log('↩️ Changes discarded');
}

/**
 * Reset all settings to defaults
 */
function resetAdminDefaults() {
    if (!confirm('⚠️ Reset ALL admin settings to defaults? This cannot be undone!')) {
        return;
    }
    
    if (!confirm('Are you absolutely sure? This will overwrite all current settings.')) {
        return;
    }
    
    adminSettings = getDefaultAdminSettings();
    populateAllSections();
    hasUnsavedChanges = true;
    document.getElementById('unsaved-indicator').style.display = 'block';
    
    alert('⚠️ Settings reset to defaults. Click Save to apply changes.');
    console.log('🔄 Reset to defaults');
}

/**
 * Trigger manual backup
 */
async function triggerManualBackup() {
    if (!confirm('Trigger a manual backup now?')) {
        return;
    }
    
    try {
        console.log('💾 Triggering manual backup...');
        
        const response = await fetch('/api/admin/backup/manual', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Backup request failed');
        }
        
        const data = await response.json();
        
        alert(`✅ Backup completed successfully!\nFile: ${data.filename}\nSize: ${data.size}`);
        console.log('✅ Backup completed:', data);
        
    } catch (error) {
        console.error('❌ Error triggering backup:', error);
        alert(`Failed to trigger backup: ${error.message}`);
    }
}
