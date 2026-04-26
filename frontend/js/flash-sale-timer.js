/**
 * Flash Sale Timer - Real-time countdown for flash sale products
 * Finds all timer elements and updates them every second
 */

class FlashSaleTimer {
    constructor() {
        this.timers = new Map();
        this.init();
    }

    /**
     * Initialize all timers on the page
     */
    init() {
        const timerElements = document.querySelectorAll('[data-sale-ends-at]');
        timerElements.forEach(el => {
            const saleEndsAt = el.getAttribute('data-sale-ends-at');
            const productId = el.getAttribute('data-product-id');
            
            if (saleEndsAt && productId) {
                this.addTimer(productId, saleEndsAt, el);
                // Initial update
                this.updateTimer(productId);
            }
        });

        // Update all timers every second
        setInterval(() => this.updateAllTimers(), 1000);
    }

    /**
     * Add a new timer to track
     */
    addTimer(productId, saleEndsAt, element) {
        this.timers.set(productId, {
            saleEndsAt: new Date(saleEndsAt),
            elements: this.timers.has(productId) 
                ? [...this.timers.get(productId).elements, element]
                : [element]
        });
    }

    /**
     * Update all timer displays
     */
    updateAllTimers() {
        this.timers.forEach((timer, productId) => {
            this.updateTimer(productId);
        });
    }

    /**
     * Update a specific timer
     */
    updateTimer(productId) {
        const timer = this.timers.get(productId);
        if (!timer) return;

        const now = new Date();
        const timeLeft = timer.saleEndsAt - now;

        if (timeLeft <= 0) {
            // Sale has ended
            this.handleSaleEnded(productId, timer.elements);
            return;
        }

        // Calculate time units
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

        // Update all elements for this product
        timer.elements.forEach(el => {
            this.renderTimer(el, { days, hours, minutes, seconds, timeLeft });
        });
    }

    /**
     * Render timer display
     */
    renderTimer(element, timeData) {
        const { days, hours, minutes, seconds, timeLeft } = timeData;

        // Determine urgency level
        let urgencyClass = 'timer-normal';
        if (timeLeft < 3600000) { // Less than 1 hour
            urgencyClass = 'timer-urgent';
        } else if (timeLeft < 86400000) { // Less than 1 day
            urgencyClass = 'timer-warning';
        }

        // Format display
        let displayText = '';
        if (days > 0) {
            displayText = `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            displayText = `${hours}h ${minutes}m ${seconds}s`;
        } else if (minutes > 0) {
            displayText = `${minutes}m ${seconds}s`;
        } else {
            displayText = `${seconds}s`;
        }

        // Update element
        element.textContent = displayText;
        element.className = `flash-sale-timer ${urgencyClass}`;
    }

    /**
     * Handle when sale has ended
     */
    handleSaleEnded(productId, elements) {
        elements.forEach(el => {
            el.textContent = 'Sale Ended';
            el.className = 'flash-sale-timer timer-expired';
            
            // Fade out and hide the timer
            el.style.opacity = '0.5';
            el.style.pointerEvents = 'none';
            
            // Hide the badge container if it exists
            const badgeContainer = el.closest('.flash-sale-badge');
            if (badgeContainer) {
                setTimeout(() => {
                    badgeContainer.style.display = 'none';
                }, 1000);
            }
        });

        // Stop tracking this timer
        this.timers.delete(productId);
    }
}

// Initialize timer when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new FlashSaleTimer();
    });
} else {
    // DOM is already loaded
    new FlashSaleTimer();
}

// Support for dynamically added products (e.g., AJAX)
window.FlashSaleTimer = FlashSaleTimer;
