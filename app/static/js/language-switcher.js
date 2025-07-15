
/* Enhanced Language Switcher for Smart Agriculture App */
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize language functionality
    initializeLanguageSwitcher();
    
    function initializeLanguageSwitcher() {
        // Set up language dropdown toggles
        window.toggleLanguageDropdown = function() {
            const authDropdown = document.getElementById('authLanguageDropdown');
            const guestDropdown = document.getElementById('guestLanguageDropdown');
            
            if (authDropdown && !authDropdown.classList.contains('hidden')) {
                authDropdown.classList.add('hidden');
            } else if (authDropdown) {
                authDropdown.classList.remove('hidden');
                // Close guest dropdown if open
                if (guestDropdown) guestDropdown.classList.add('hidden');
            }
            
            if (guestDropdown && !guestDropdown.classList.contains('hidden')) {
                guestDropdown.classList.add('hidden');
            } else if (guestDropdown) {
                guestDropdown.classList.remove('hidden');
                // Close auth dropdown if open
                if (authDropdown) authDropdown.classList.add('hidden');
            }
        };
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', function(event) {
            const isLanguageButton = event.target.closest('[onclick*="toggleLanguageDropdown"]');
            const isDropdown = event.target.closest('#authLanguageDropdown, #guestLanguageDropdown');
            
            if (!isLanguageButton && !isDropdown) {
                closeAllLanguageDropdowns();
            }
        });
        
        // Close dropdowns on escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeAllLanguageDropdowns();
            }
        });
        
        // Enhanced language switching with loading indicator
        window.switchLanguage = function(language, event) {
            if (event) {
                event.preventDefault();
            }
            
            // Store preference in localStorage
            localStorage.setItem('preferredLanguage', language);
            
            // Show loading indicator
            showLanguageLoadingIndicator(language);
            
            // Navigate to language switcher
            setTimeout(() => {
                window.location.href = `/set-language/${language}`;
            }, 300);
        };
        
        // Apply ARIA attributes for accessibility
        enhanceAccessibility();
        
        // Set up smooth language transitions
        setupLanguageTransitions();
    }
    
    function closeAllLanguageDropdowns() {
        const authDropdown = document.getElementById('authLanguageDropdown');
        const guestDropdown = document.getElementById('guestLanguageDropdown');
        
        if (authDropdown) authDropdown.classList.add('hidden');
        if (guestDropdown) guestDropdown.classList.add('hidden');
    }
    
    function showLanguageLoadingIndicator(language) {
        const loadingText = language === 'hi' ? 'भाषा बदली जा रही है...' : 'Switching language...';
        
        const indicator = document.createElement('div');
        indicator.id = 'language-loading-indicator';
        indicator.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        indicator.innerHTML = `
            <div class="bg-white rounded-lg p-6 flex items-center space-x-3 shadow-xl">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="text-gray-700 font-medium">${loadingText}</span>
            </div>
        `;
        
        document.body.appendChild(indicator);
        
        // Remove after timeout (failsafe)
        setTimeout(() => {
            const existingIndicator = document.getElementById('language-loading-indicator');
            if (existingIndicator) {
                existingIndicator.remove();
            }
        }, 5000);
    }
    
    function enhanceAccessibility() {
        // Add ARIA labels to language buttons
        const languageButtons = document.querySelectorAll('[onclick*="toggleLanguageDropdown"]');
        languageButtons.forEach(button => {
            button.setAttribute('aria-label', 'Change language');
            button.setAttribute('aria-expanded', 'false');
            button.setAttribute('aria-haspopup', 'true');
        });
        
        // Add ARIA labels to language links
        const languageLinks = document.querySelectorAll('a[href*="/set-language/"]');
        languageLinks.forEach(link => {
            const lang = link.href.includes('/hi') ? 'Hindi' : 'English';
            link.setAttribute('aria-label', `Switch to ${lang}`);
        });
    }
    
    function setupLanguageTransitions() {
        // Add smooth transition classes to elements that might change
        const elementsToTransition = document.querySelectorAll('body, main, .container');
        elementsToTransition.forEach(el => {
            el.style.transition = 'opacity 0.2s ease-in-out';
        });
    }
    
    // Auto-apply saved language preference - COMPLETELY DISABLED
    function applySavedLanguagePreference() {
        // COMPLETELY DISABLED: No automatic language switching to prevent server conflicts
        // Language is now controlled entirely by server-side Flask-Babel
        // User language preference is handled by the Flask route /set-language/<language>
        console.log('Auto language switching completely disabled - using server-side language only');
        return;
    }
    
    // DISABLED: Don't initialize saved language preference
    // applySavedLanguagePreference();
    
    // Update language button states based on server-side language
    function updateLanguageButtonStates() {
        // Use server-set language from window.currentLanguage (set in base.html)
        const currentLang = window.currentLanguage || document.documentElement.lang || 'hi';
        const languageButtons = document.querySelectorAll('[onclick*="toggleLanguageDropdown"]');
        
        console.log('Updating language buttons for language:', currentLang);
        
        languageButtons.forEach(button => {
            const text = currentLang === 'hi' ? '🇮🇳 हिंदी' : '🇺🇸 English';
            button.innerHTML = text + ' <svg class="ml-1 h-4 w-4 inline" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
        });
    }
    
    updateLanguageButtonStates();
    
    // Set document language attribute from server-side setting
    function setDocumentLanguage() {
        // Use server-set language from window.currentLanguage
        const currentLang = window.currentLanguage || document.documentElement.lang || 'hi';
        document.documentElement.setAttribute('lang', currentLang);
        
        console.log('Document language set to:', currentLang);
        
        // Set text direction for future RTL support
        document.documentElement.setAttribute('dir', 'ltr');
    }
    
    setDocumentLanguage();
    
    // Debug function for development
    window.debugLanguageSystem = function() {
        console.log('=== Language System Debug ===');
        console.log('Server-side language (window.currentLanguage):', window.currentLanguage);
        console.log('Document language attribute:', document.documentElement.lang);
        console.log('LocalStorage preference:', localStorage.getItem('preferredLanguage'));
        console.log('Session switching flag:', sessionStorage.getItem('justSwitchedLanguage'));
        console.log('Language auto-switching: DISABLED');
        console.log('Current URL:', window.location.href);
        console.log('Language dropdowns:', {
            auth: !!document.getElementById('authLanguageDropdown'),
            guest: !!document.getElementById('guestLanguageDropdown')
        });
        console.log('==============================');
    };
});

/* CSS for smooth language transitions */
const style = document.createElement('style');
style.textContent = `
    #language-loading-indicator {
        backdrop-filter: blur(2px);
    }
    
    .language-dropdown {
        transform-origin: top right;
        transition: all 0.2s ease-in-out;
    }
    
    .language-dropdown.hidden {
        opacity: 0;
        transform: scale(0.95) translateY(-10px);
        pointer-events: none;
    }
    
    .language-dropdown:not(.hidden) {
        opacity: 1;
        transform: scale(1) translateY(0);
        pointer-events: auto;
    }
    
    /* Improved focus styles for accessibility */
    button[onclick*="toggleLanguageDropdown"]:focus,
    a[href*="/set-language/"]:focus {
        outline: 2px solid #3B82F6;
        outline-offset: 2px;
        border-radius: 4px;
    }
    
    /* Loading animation enhancement */
    @keyframes language-switch-fade {
        from { opacity: 1; }
        to { opacity: 0.7; }
    }
    
    .language-switching body {
        animation: language-switch-fade 0.3s ease-in-out;
    }
`;
document.head.appendChild(style);
