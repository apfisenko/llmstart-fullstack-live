---
name: nextjs-app-router-patterns
description: >-
  Соглашения и паттерны Next.js App Router: `app/`, layouts, сегменты, special
  files, Route Handlers, группы и динамика. Используй при проектировании
  маршрутов, вложенных layout, loading/error UI, `route.ts`, когда пользователь
  упоминает App Router или `/nextjs-app-router-patterns`.
---

# Next.js App Router — паттерны

## Корень `app/`

- **`layout.tsx`** — оболочка сегмента и дочерних сегментов; сохраняет состояние при навигации между страницами сегмента; вложенные layout складываются матрёшкой.
- **`template.tsx`** — как layout, но **ремонтируется** при смене дочернего URL; нужен для enter/exit-анимаций или сброса локального состояния при каждой навигации.
- **`page.tsx`** — лист маршрута; обязателен, чтобы сегмент был доступен как URL (кроме случаев с `@slot` + `default.tsx`).
- **`default.tsx`** — fallback для **optional parallel segments** (`@modal` и т.п.).

## Special files (UX и границы)

- **`loading.tsx`** — обёртка в Suspense для сегмента; стриминг UI «скелетонов» без блокировки всего дерева.
- **`error.tsx`** — Error Boundary сегмента; должен быть **client component**; изолирует сбои дочерних частей.
- **`not-found.tsx`** — UI 404 для сегмента; для явного вызова использовать `notFound()` из `next/navigation`.
- Имена **резервируются** фреймворком — не использовать их для произвольных модулей в том же смысле.

## Данные рядом с маршрутом

- **`generateMetadata` / `metadata`** — рядом с `page`/`layout` сегмента; тяжёлая логика — в `generateMetadata`, статика — в `metadata`.
- **`generateStaticParams`** — для статической генерации динамических сегментов `[slug]` при билде (когда применимо).

## Динамика и группы

- **`[param]`** — один сегмент; **`[...param]`** — catch-all; **`[[...param]]`** — optional catch-all.
- В свежих мажорных версиях Next **`params`** (и иногда `searchParams`) в `page`/`layout` могут приходить как **`Promise`** — использовать `await` согласно типам и доке той версии, на которой проект.
- **`(folder)`** — **route groups**: организация файлов и отдельные корневые layout без влияния на URL.
- Не злоупотреблять глубокой вложенностью без нужды — URL и файловая структура должны оставаться читаемыми.

## Route Handlers

- **`route.ts`** — **HTTP** GET/POST/… для URL этого сегмента; в **одной папке сегмента** не держать вместе **`page.tsx` и `route.ts`** — leaf на один путь должен быть один (страница или API), иначе конфликт при сборке.
- Публичные API обычно выносят в отдельный сегмент (`app/api/.../route.ts`) рядом со страницами без коллизии путей.
- Валидация входа, коды ответов, CORS — явно и минимально (KISS).

## Навигация

- **`Link`** из `next/link` — клиентская навигация и префетч по умолчанию для ссылок во viewport; отключать префетч только при веской причине.
- **`useRouter`**, **`usePathname`**, **`useSearchParams`** — в client components; серверная навигация — `redirect()` / `notFound()` из `next/navigation`.

## Связь с другими skills

- Серверные компоненты, кэш `fetch`, деплой на Vercel — см. **`vercel-react-best-practice`**.
- UI-компоненты — **`shadcn-ui`**.

## Актуальность

- Детали API (особенно parallel/intercepting routes и коллизии файлов) зависят от версии Next — при расхождении с моделью сверяться с [https://nextjs.org/docs/app](https://nextjs.org/docs/app).
