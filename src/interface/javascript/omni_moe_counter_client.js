// OMNI MOTHER: Moe-Counter Client Logic (Production Grade)
// Robust frontend embed script for fetching and rendering visitor statistics.
// Includes IntersectionObserver for lazy loading, exponential backoff for retries.

const OmniMoeCounterClient = (function() {
    let siteIdentifier = "";
    let themePath = "/assets/moe-theme";
    let isRendered = false;
    let observer = null;
    let retryCount = 0;
    const MAX_RETRIES = 5;

    function init(siteId, options = {}) {
        siteIdentifier = siteId;
        if (options.themePath) themePath = options.themePath;
        
        console.log(`[OMNI COUNTER] Initializing tracking for ${siteIdentifier}`);
        
        const container = document.querySelector('.omni-moe-counter-container');
        if (!container) {
            console.error("[OMNI COUNTER] Container .omni-moe-counter-container not found in DOM.");
            return;
        }

        // Lazy load the counter when it scrolls into view
        if ('IntersectionObserver' in window) {
            observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !isRendered) {
                        fetchCount();
                        observer.unobserve(entry.target);
                    }
                });
            }, { rootMargin: "50px" });
            observer.observe(container);
        } else {
            // Fallback for older browsers
            fetchCount();
        }
    }

    async function fetchCount() {
        if (isRendered) return;
        
        try {
            // In a real environment, this connects to the Go/PHP backend
            const response = await fetch(`https://api.omni-framework.dev/counter/v1/hits/${siteIdentifier}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ referrer: document.referrer || "direct" })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            renderDigits(data.hits || 0);
            isRendered = true;
            retryCount = 0;
            
        } catch (error) {
            console.error(`[OMNI COUNTER] Fetch failed:`, error);
            if (retryCount < MAX_RETRIES) {
                retryCount++;
                const backoffMs = Math.pow(2, retryCount) * 1000;
                console.log(`[OMNI COUNTER] Retrying in ${backoffMs}ms...`);
                setTimeout(fetchCount, backoffMs);
            } else {
                console.error("[OMNI COUNTER] Max retries reached. Displaying fallback.");
                renderDigits("ERROR");
            }
        }
    }

    function renderDigits(value) {
        const container = document.getElementById("omni-moe-digits");
        if (!container) return;
        
        container.innerHTML = "";
        const numStr = value.toString();
        
        // Document fragment to minimize reflows
        const fragment = document.createDocumentFragment();
        
        for (let i = 0; i < numStr.length; i++) {
            const char = numStr[i];
            
            if (char === "E" || char === "R" || char === "O") {
                const span = document.createElement("span");
                span.textContent = char;
                span.style.color = "red";
                fragment.appendChild(span);
                continue;
            }
            
            const img = document.createElement("img");
            img.src = `${themePath}/digit-${char}.svg`;
            img.className = "omni-moe-digit-img";
            img.alt = char;
            
            // Add CSS animation hook
            img.style.animation = `popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) ${i * 0.1}s forwards`;
            img.style.opacity = "0";
            
            fragment.appendChild(img);
        }
        
        container.appendChild(fragment);
        console.log(`[OMNI COUNTER] Rendered value: ${value}`);
    }

    return {
        init: init
    };
})();

// Auto-initialize if data attribute is present on the script tag
if (typeof document !== 'undefined' && document.currentScript && document.currentScript.dataset.siteId) {
    OmniMoeCounterClient.init(document.currentScript.dataset.siteId);
}
