const CACHE_NAME = 'expense-flow-v1';
const ASSETS = [
    '/',
    '/static/images/favicon.png'
];

// Installs the service worker and caches core layout shells
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

// Listens to fetch requests so the app launches instantly
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});