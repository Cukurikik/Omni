// Guess.js inspired Prefetcher Worker
self.onmessage = async (event) => {
    const { routes } = event.data;
    if (!routes || !Array.isArray(routes)) return;

    for (const route of routes) {
        try {
            const response = await fetch(route, { priority: 'low' });
            if (response.ok) {
                self.postMessage({ route, status: 'prefetched' });
            }
        } catch (err) {
            self.postMessage({ route, error: err.message });
        }
    }
};
