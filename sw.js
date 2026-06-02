/* AZL Universe Explorer — Service Worker v2 (offline-first) */
const CACHE = 'azl-universe-v2';
const CORE  = [
  '/universe',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

/* Install: pre-cache all core assets */
self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(c => {
      return Promise.allSettled(CORE.map(url =>
        c.add(url).catch(err => console.warn('[SW] failed to cache', url, err))
      ));
    })
  );
});

/* Activate: purge old caches immediately */
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

/* Fetch: cache-first for core assets, network-first for everything else */
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;

  const isCoreAsset = CORE.includes(url.pathname) ||
    url.pathname.startsWith('/icon-') ||
    url.pathname === '/sw.js';

  if (isCoreAsset) {
    /* Cache-first: serve instantly offline */
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(res => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
          }
          return res;
        });
      })
    );
  } else {
    /* Network-first with cache fallback */
    e.respondWith(
      fetch(e.request)
        .then(res => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, clone));
          }
          return res;
        })
        .catch(() => caches.match(e.request))
    );
  }
});
