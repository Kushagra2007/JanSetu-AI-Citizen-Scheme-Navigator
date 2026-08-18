const CACHE_NAME = 'csn-cache-v2';
const ASSETS = ['/static/css/style.css', '/static/js/app.js', '/static/manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
  )).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request).catch(() => cached))
  );
});

self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'Citizen Service Navigator', body: 'You have a new update.' };
  event.waitUntil(self.registration.showNotification(data.title, { body: data.body, icon: '/static/icon.png' }));
});
