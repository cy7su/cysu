// Service Worker для кэширования статических ресурсов
const CACHE_NAME = 'cysu-v5'
const STATIC_CACHE = 'cysu-static-v5'

// Ресурсы для кэширования (с версиями)
const STATIC_RESOURCES = [
    '/static/css/style.css?v=4',
    '/static/css/admin.css?v=4',
    '/static/js/svg-patterns.js?v=4',
    '/static/icons/favicon-48x48.png?v=4',
    '/static/icons/android-chrome-192x192.png?v=3',
    '/static/site.webmanifest?v=3',
    '/static/favicon.ico?v=4',
]

// Установка Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches
            .open(STATIC_CACHE)
            .then((cache) => {
                return cache.addAll(STATIC_RESOURCES)
            })
            .then(() => {
                return self.skipWaiting()
            }),
    )
})

// Активация Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches
            .keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== CACHE_NAME) {
                            return caches.delete(cacheName)
                        }
                    }),
                )
            })
            .then(() => {
                return self.clients.claim()
            }),
    )
})

// Перехват запросов
self.addEventListener('fetch', (event) => {
    // Только GET запросы
    if (event.request.method !== 'GET') {
        return
    }

    // Игнорируем запросы к API
    if (event.request.url.includes('/api/')) {
        return
    }

    event.respondWith(
        caches.match(event.request).then((response) => {
            // Если ресурс в кэше, возвращаем его
            if (response) {
                return response
            }

            // Иначе загружаем из сети
            return fetch(event.request).then((response) => {
                // Проверяем валидность ответа
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response
                }

                // Кэшируем только статические ресурсы
                if (event.request.url.includes('/static/')) {
                    const responseToCache = response.clone()
                    caches.open(STATIC_CACHE).then((cache) => {
                        cache.put(event.request, responseToCache)
                    })
                }

                return response
            })
        }),
    )
})
