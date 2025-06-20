// Service Worker for Wisbee PWA
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
    // シンプルなネットワークファーストストラテジー
    event.respondWith(fetch(event.request));
});