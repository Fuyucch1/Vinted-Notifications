/**
 * Navigation Component JavaScript
 * Handles sidebar collapse, dark mode toggle, and responsive navigation
 */

class NavigationController {
    constructor() {
        this.sidebar = document.getElementById('desktopSidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.darkModeToggle = document.getElementById('darkModeToggle');
        this.mainContent = document.querySelector('.main-content');
        
        // Storage keys
        this.SIDEBAR_STATE_KEY = 'vinted-sidebar-collapsed';
        this.DARK_MODE_KEY = 'vinted-dark-mode';
        
        this.init();
    }
    
    init() {
        this.initSidebarToggle();
        this.initDarkMode();
        this.initTooltips();
        this.initResponsiveHandling();
        this.restoreUserPreferences();
    }
    
    /**
     * Initialize sidebar collapse functionality
     */
    initSidebarToggle() {
        if (!this.sidebarToggle || !this.sidebar) return;
        
        this.sidebarToggle.addEventListener('click', () => {
            this.toggleSidebar();
        });
        
        // Handle keyboard navigation
        this.sidebarToggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleSidebar();
            }
        });
    }
    
    /**
     * Toggle sidebar collapsed state
     */
    toggleSidebar() {
        const isCollapsed = this.sidebar.classList.contains('collapsed');
        
        if (isCollapsed) {
            this.expandSidebar();
        } else {
            this.collapseSidebar();
        }
        
        // Save state to localStorage
        try {
            localStorage.setItem(this.SIDEBAR_STATE_KEY, (!isCollapsed).toString());
        } catch (e) {
            console.warn('Failed to save sidebar state:', e);
        }
    }
    
    /**
     * Collapse the sidebar
     */
    collapseSidebar() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.add('collapsed');
        if (this.mainContent) {
            this.mainContent.classList.add('sidebar-collapsed');
        }
        
        // Update toggle button icon
        if (this.sidebarToggle) {
            const icon = this.sidebarToggle.querySelector('i');
            if (icon) {
                icon.className = 'bi bi-arrow-right fs-5';
            }
            
            // Update tooltip
            this.sidebarToggle.setAttribute('title', 'Expand Sidebar');
            this.updateTooltip(this.sidebarToggle);
        }
        
        // Enable tooltips for nav items when collapsed
        this.toggleNavTooltips(true);
    }
    
    /**
     * Expand the sidebar
     */
    expandSidebar() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.remove('collapsed');
        if (this.mainContent) {
            this.mainContent.classList.remove('sidebar-collapsed');
        }
        
        // Update toggle button icon
        if (this.sidebarToggle) {
            const icon = this.sidebarToggle.querySelector('i');
            if (icon) {
                icon.className = 'bi bi-list fs-5';
            }
            
            // Update tooltip
            this.sidebarToggle.setAttribute('title', 'Collapse Sidebar');
            this.updateTooltip(this.sidebarToggle);
        }
        
        // Disable tooltips for nav items when expanded
        this.toggleNavTooltips(false);
    }
    
    /**
     * Toggle navigation item tooltips
     */
    toggleNavTooltips(enable) {
        if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) {
            return;
        }
        
        // Store tooltip-enabled elements when disabling, or use all nav links when enabling
        if (enable) {
            // When enabling, select all nav links that should have tooltips
            const navLinks = this.sidebar.querySelectorAll('.nav-link');
            
            navLinks.forEach(link => {
                try {
                    // Check if tooltip already exists before creating new one
                    const existingTooltip = bootstrap.Tooltip.getInstance(link);
                    if (existingTooltip) {
                        return; // Skip if already has tooltip
                    }
                    // Enable tooltip
                    link.setAttribute('data-bs-toggle', 'tooltip');
                    new bootstrap.Tooltip(link);
                } catch (e) {
                    console.warn('Failed to enable nav tooltip:', e);
                }
            });
        } else {
            // When disabling, only target those that currently have tooltips
            const navLinks = this.sidebar.querySelectorAll('.nav-link[data-bs-toggle="tooltip"]');
            
            navLinks.forEach(link => {
                try {
                    // Disable tooltip
                    const tooltip = bootstrap.Tooltip.getInstance(link);
                    if (tooltip) {
                        tooltip.dispose();
                    }
                    link.removeAttribute('data-bs-toggle');
                } catch (e) {
                    console.warn('Failed to disable nav tooltip:', e);
                }
            });
        }
    }
    
    /**
     * Initialize dark mode functionality
     */
    initDarkMode() {
        if (!this.darkModeToggle) return;
        
        this.darkModeToggle.addEventListener('change', () => {
            this.toggleDarkMode();
        });
    }
    
    /**
     * Toggle dark mode
     */
    toggleDarkMode() {
        const html = document.documentElement;
        const isDark = this.darkModeToggle.checked;
        
        if (isDark) {
            html.setAttribute('data-bs-theme', 'dark');
        } else {
            html.setAttribute('data-bs-theme', 'light');
        }
        
        // Save preference to localStorage
        try {
            localStorage.setItem(this.DARK_MODE_KEY, isDark.toString());
        } catch (e) {
            console.warn('Failed to save dark mode preference:', e);
        }
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: isDark ? 'dark' : 'light' }
        }));
    }
    
    /**
     * Initialize Bootstrap tooltips
     */
    initTooltips() {
        // Check if Bootstrap is available
        if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) {
            console.warn('Bootstrap tooltips not available');
            return;
        }
        
        // Initialize tooltips for elements that should always have them
        const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]:not(.nav-link)');
        tooltipElements.forEach(element => {
            try {
                new bootstrap.Tooltip(element);
            } catch (e) {
                console.warn('Failed to initialize tooltip:', e);
            }
        });
    }
    
    /**
     * Update existing tooltip
     */
    updateTooltip(element) {
        if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) {
            return;
        }
        
        try {
            const tooltip = bootstrap.Tooltip.getInstance(element);
            if (tooltip) {
                tooltip.dispose();
            }
            new bootstrap.Tooltip(element);
        } catch (e) {
            console.warn('Failed to update tooltip:', e);
        }
    }
    
    /**
     * Handle responsive behavior
     */
    initResponsiveHandling() {
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
        
        // Handle mobile tab bar active states
        this.initMobileTabBar();
    }
    
    /**
     * Handle window resize events
     */
    handleResize() {
        const isMobile = window.innerWidth < 768;
        
        if (isMobile) {
            // On mobile, ensure sidebar is not affecting layout
            if (this.mainContent) {
                this.mainContent.classList.remove('sidebar-collapsed');
            }
        } else {
            // On desktop, restore sidebar state
            const isCollapsed = this.sidebar.classList.contains('collapsed');
            if (this.mainContent) {
                if (isCollapsed) {
                    this.mainContent.classList.add('sidebar-collapsed');
                } else {
                    this.mainContent.classList.remove('sidebar-collapsed');
                }
            }
        }
    }
    
    /**
     * Initialize mobile tab bar functionality
     */
    initMobileTabBar() {
        const tabLinks = document.querySelectorAll('.mobile-tab-bar .tab-link');
        
        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Add visual feedback for touch
                link.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    link.style.transform = '';
                }, 150);
            });
        });
    }
    
    /**
     * Restore user preferences from localStorage
     */
    restoreUserPreferences() {
        try {
            // Restore sidebar state
            const sidebarCollapsed = localStorage.getItem(this.SIDEBAR_STATE_KEY) === 'true';
            if (sidebarCollapsed && window.innerWidth >= 768 && this.sidebar && this.sidebarToggle) {
                this.collapseSidebar();
            }
            
            // Restore dark mode
            const darkMode = localStorage.getItem(this.DARK_MODE_KEY) === 'true';
            if (this.darkModeToggle) {
                this.darkModeToggle.checked = darkMode;
                if (darkMode) {
                    document.documentElement.setAttribute('data-bs-theme', 'dark');
                    // Dispatch theme change event on initial load
                    window.dispatchEvent(new CustomEvent('themeChanged', {
                        detail: { theme: 'dark' }
                    }));
                }
            }
        } catch (e) {
            console.warn('Failed to restore user preferences:', e);
        }
    }
    
    /**
     * Get current theme
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-bs-theme') || 'light';
    }
    
    /**
     * Get sidebar state
     */
    isSidebarCollapsed() {
        if (!this.sidebar) return false;
        return this.sidebar.classList.contains('collapsed');
    }
    
    /**
     * Public method to programmatically set dark mode
     */
    setDarkMode(enabled) {
        if (this.darkModeToggle) {
            this.darkModeToggle.checked = enabled;
            this.toggleDarkMode();
        }
    }
    
    /**
     * Public method to programmatically set sidebar state
     */
    setSidebarCollapsed(collapsed) {
        if (collapsed && !this.isSidebarCollapsed()) {
            this.collapseSidebar();
        } else if (!collapsed && this.isSidebarCollapsed()) {
            this.expandSidebar();
        }
    }
}

// Utility functions for external use
window.NavigationUtils = {
    /**
     * Highlight active navigation item based on current path
     */
    updateActiveNavigation: function(currentPath) {
        // Update desktop sidebar
        const desktopLinks = document.querySelectorAll('.desktop-sidebar .nav-link');
        desktopLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
        
        // Update mobile tab bar
        const mobileLinks = document.querySelectorAll('.mobile-tab-bar .tab-link');
        mobileLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    },
    
    /**
     * Show notification badge on navigation item
     */
    showNotificationBadge: function(navItem, count) {
        const links = document.querySelectorAll(`[href="${navItem}"]`);
        links.forEach(link => {
            let badge = link.querySelector('.notification-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'notification-badge badge bg-danger rounded-pill ms-auto';
                badge.style.fontSize = '0.75rem';
                link.appendChild(badge);
            }
            badge.textContent = count > 99 ? '99+' : count.toString();
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });
    },
    
    /**
     * Hide notification badge
     */
    hideNotificationBadge: function(navItem) {
        const links = document.querySelectorAll(`[href="${navItem}"]`);
        links.forEach(link => {
            const badge = link.querySelector('.notification-badge');
            if (badge) {
                badge.style.display = 'none';
            }
        });
    }
};

// Initialize navigation when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation controller
    window.navigationController = new NavigationController();
    
    // Handle page visibility changes to update active states
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            NavigationUtils.updateActiveNavigation(window.location.pathname);
        }
    });
    
    // Handle browser back/forward navigation
    window.addEventListener('popstate', function() {
        NavigationUtils.updateActiveNavigation(window.location.pathname);
    });
});

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NavigationController, NavigationUtils };
}