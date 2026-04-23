const CACHE_NAME = 'insight-cache-v2';
const urlsToCache = [
  '/',
  '/index.html',
  '/dashboard.html',
  '/trading.html',
  '/login.html',
  '/js/app.js',
  '/js/api.js',
  '/js/auth.js',
  '/manifest.json'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/api/')) return;
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request).then(
          function(response) {
            if(!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            var responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(function(cache) {
                cache.put(event.request, responseToCache);
              });
            return response;
          }
        );
      })
  );
});

self.addEventListener('push', event => {
  const data = event.data.json();
  self.registration.showNotification(data.title, {
    body: data.body,
    icon: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Blue_diamond.svg/512px-Blue_diamond.svg.png',
    vibrate: [200, 100, 200, 100, 200, 100, 200]
  });
});
