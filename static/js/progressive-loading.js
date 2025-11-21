/**
 * Progressive Loading Framework - Client Side
 * Enables fast page loads with progressive data loading
 */

class ProgressiveLoader {
    constructor() {
        this.loadingStates = new Map();
        this.retryAttempts = new Map();
        this.maxRetries = 3;
        this.loadingIndicators = new Set();
    }

    /**
     * Show loading skeleton for immediate visual feedback
     */
    showLoadingSkeleton(containerId, type = 'generic') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const skeletons = {
            generic: this.createGenericSkeleton(),
            table: this.createTableSkeleton(),
            cards: this.createCardsSkeleton(),
            dashboard: this.createDashboardSkeleton()
        };

        container.innerHTML = skeletons[type] || skeletons.generic;
        this.loadingStates.set(containerId, true);
    }

    /**
     * Load data progressively and update UI
     */
    async loadData(endpoint, containerId, updateCallback, options = {}) {
        const {
            showSkeleton = true,
            retryOnError = true,
            cacheKey = null,
            ttl = 60000 // 1 minute default
        } = options;

        // Show loading skeleton immediately
        if (showSkeleton) {
            this.showLoadingSkeleton(containerId, options.skeletonType);
        }

        try {
            // Check cache first
            if (cacheKey) {
                const cached = this.getCachedData(cacheKey, ttl);
                if (cached) {
                    updateCallback(cached, containerId);
                    this.loadingStates.set(containerId, false);
                    return;
                }
            }

            // Start loading indicator
            this.startLoadingIndicator(containerId);

            // Fetch data
            const response = await fetch(endpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Cache the data if cache key provided
            if (cacheKey) {
                this.setCachedData(cacheKey, data);
            }

            // Update UI with data
            updateCallback(data, containerId);

            // Reset retry count on success
            this.retryAttempts.delete(endpoint);
            
        } catch (error) {
            console.error(`❌ Error loading data from ${endpoint}:`, error);
            
            // Retry logic
            if (retryOnError) {
                const attempts = this.retryAttempts.get(endpoint) || 0;
                if (attempts < this.maxRetries) {
                    this.retryAttempts.set(endpoint, attempts + 1);
                    console.log(`🔄 Retrying ${endpoint} (attempt ${attempts + 1}/${this.maxRetries})`);
                    
                    // Exponential backoff
                    const delay = Math.pow(2, attempts) * 1000;
                    setTimeout(() => {
                        this.loadData(endpoint, containerId, updateCallback, options);
                    }, delay);
                    return;
                }
            }

            // Show error state
            this.showError(containerId, error.message);
        } finally {
            this.stopLoadingIndicator(containerId);
            this.loadingStates.set(containerId, false);
        }
    }

    /**
     * Create loading skeletons
     */
    createGenericSkeleton() {
        return `
            <div class="loading-skeleton">
                <div class="skeleton-item skeleton-text"></div>
                <div class="skeleton-item skeleton-text short"></div>
                <div class="skeleton-item skeleton-text medium"></div>
            </div>
        `;
    }

    createTableSkeleton() {
        return `
            <div class="loading-skeleton">
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th><div class="skeleton-item skeleton-text short"></div></th>
                                <th><div class="skeleton-item skeleton-text short"></div></th>
                                <th><div class="skeleton-item skeleton-text short"></div></th>
                                <th><div class="skeleton-item skeleton-text short"></div></th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Array.from({length: 5}, () => `
                                <tr>
                                    <td><div class="skeleton-item skeleton-text"></div></td>
                                    <td><div class="skeleton-item skeleton-text"></div></td>
                                    <td><div class="skeleton-item skeleton-text"></div></td>
                                    <td><div class="skeleton-item skeleton-text"></div></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    createCardsSkeleton() {
        return `
            <div class="row loading-skeleton">
                ${Array.from({length: 4}, () => `
                    <div class="col-md-3 mb-4">
                        <div class="card">
                            <div class="card-body">
                                <div class="skeleton-item skeleton-text short"></div>
                                <div class="skeleton-item skeleton-text large"></div>
                                <div class="skeleton-item skeleton-text medium"></div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    createDashboardSkeleton() {
        return `
            <div class="row loading-skeleton">
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <div class="skeleton-item skeleton-text short"></div>
                            <div class="skeleton-item skeleton-text large"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <div class="skeleton-item skeleton-text short"></div>
                            <div class="skeleton-item skeleton-text large"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <div class="skeleton-item skeleton-text short"></div>
                            <div class="skeleton-item skeleton-text large"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <div class="skeleton-item skeleton-text short"></div>
                            <div class="skeleton-item skeleton-text large"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Loading indicators
     */
    startLoadingIndicator(containerId) {
        const indicator = document.createElement('div');
        indicator.id = `loading-${containerId}`;
        indicator.className = 'loading-indicator';
        indicator.innerHTML = `
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span class="ms-2">Loading...</span>
        `;
        
        const container = document.getElementById(containerId);
        if (container && !document.getElementById(indicator.id)) {
            container.insertBefore(indicator, container.firstChild);
            this.loadingIndicators.add(indicator.id);
        }
    }

    stopLoadingIndicator(containerId) {
        const indicatorId = `loading-${containerId}`;
        const indicator = document.getElementById(indicatorId);
        if (indicator) {
            indicator.remove();
            this.loadingIndicators.delete(indicatorId);
        }
    }

    /**
     * Error handling
     */
    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Error loading data:</strong> ${message}
                <button class="btn btn-outline-danger btn-sm ms-2" onclick="location.reload()">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }

    /**
     * Simple client-side caching
     */
    getCachedData(key, ttl) {
        try {
            const cached = localStorage.getItem(`progressive_cache_${key}`);
            if (!cached) return null;

            const { data, timestamp } = JSON.parse(cached);
            const age = Date.now() - timestamp;

            if (age > ttl) {
                localStorage.removeItem(`progressive_cache_${key}`);
                return null;
            }

            console.log(`📋 Cache HIT for ${key} (age: ${Math.round(age/1000)}s)`);
            return data;
        } catch (error) {
            console.error('Cache read error:', error);
            return null;
        }
    }

    setCachedData(key, data) {
        try {
            const cacheEntry = {
                data,
                timestamp: Date.now()
            };
            localStorage.setItem(`progressive_cache_${key}`, JSON.stringify(cacheEntry));
            console.log(`📋 Cached data for ${key}`);
        } catch (error) {
            console.error('Cache write error:', error);
        }
    }

    /**
     * Clear all cached data
     */
    clearCache() {
        try {
            const keys = Object.keys(localStorage).filter(key => key.startsWith('progressive_cache_'));
            keys.forEach(key => localStorage.removeItem(key));
            console.log(`🧹 Cleared ${keys.length} cached items`);
        } catch (error) {
            console.error('Cache clear error:', error);
        }
    }

    /**
     * Check if data is currently loading
     */
    isLoading(containerId) {
        return this.loadingStates.get(containerId) || false;
    }

    /**
     * Batch load multiple endpoints
     */
    async loadMultiple(requests) {
        const promises = requests.map(request => {
            const { endpoint, containerId, updateCallback, options } = request;
            return this.loadData(endpoint, containerId, updateCallback, options);
        });

        try {
            await Promise.allSettled(promises);
            console.log(`✅ Completed batch loading of ${requests.length} requests`);
        } catch (error) {
            console.error('❌ Error in batch loading:', error);
        }
    }
}

/**
 * Pagination helper for progressive loading
 */
class ProgressivePagination {
    constructor(containerId, loadDataCallback) {
        this.containerId = containerId;
        this.loadDataCallback = loadDataCallback;
        this.currentPage = 1;
        this.totalPages = 1;
        this.isLoading = false;
    }

    async loadPage(page) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.currentPage = page;
        
        try {
            await this.loadDataCallback(page);
        } finally {
            this.isLoading = false;
        }
    }

    createPaginationControls(totalPages) {
        this.totalPages = totalPages;
        
        const paginationHtml = `
            <nav aria-label="Progressive pagination" class="mt-3">
                <ul class="pagination justify-content-center">
                    <li class="page-item ${this.currentPage <= 1 ? 'disabled' : ''}">
                        <button class="page-link" onclick="pagination.loadPage(${this.currentPage - 1})">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                    </li>
                    ${this.generatePageNumbers()}
                    <li class="page-item ${this.currentPage >= totalPages ? 'disabled' : ''}">
                        <button class="page-link" onclick="pagination.loadPage(${this.currentPage + 1})">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </li>
                </ul>
            </nav>
        `;
        
        return paginationHtml;
    }

    generatePageNumbers() {
        const pages = [];
        const maxVisible = 5;
        
        let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(this.totalPages, start + maxVisible - 1);
        
        if (end - start + 1 < maxVisible) {
            start = Math.max(1, end - maxVisible + 1);
        }
        
        for (let i = start; i <= end; i++) {
            const active = i === this.currentPage ? 'active' : '';
            pages.push(`
                <li class="page-item ${active}">
                    <button class="page-link" onclick="pagination.loadPage(${i})">${i}</button>
                </li>
            `);
        }
        
        return pages.join('');
    }
}

// Global instances
window.progressiveLoader = new ProgressiveLoader();

// Performance monitoring
window.addEventListener('load', () => {
    const loadTime = performance.now();
    console.log(`🚀 Page loaded in ${Math.round(loadTime)}ms`);
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    // Clear any pending timers or requests
    progressiveLoader.loadingIndicators.clear();
    progressiveLoader.loadingStates.clear();
    progressiveLoader.retryAttempts.clear();
});