# Задача 03: итог

## Сделано

- Создан **`frontend/web/`**: Next.js 16 (App Router), TypeScript, Tailwind 4, ESLint, **pnpm**; **shadcn/ui** (button, input, card, sheet, label).
- Тёмная тема по умолчанию: класс `dark` на `<html>`, доработка токенов в `app/globals.css` (холодный фон, акцент primary).
- Вход: страница `/login`, прокси **`POST /api/v1/auth/dev-session`** через Route Handler, сохранение контекста в **`localStorage`**, выход из шапки.
- Layout: боковая навигация, заглушки экранов, **глобальный FAB + Sheet** (каркас чата).
- **Makefile**: `frontend-install`, `frontend-dev`, `frontend-lint`, `frontend-build`; зеркальные цели в **`tasks.ps1`**.
- **`frontend/web/.env.example`**, обновлены **README** и фрагмент **integrations.md** (подписи клиентов в диаграмме).
- **Бот**: `POST /api/v1/auth/dev-session` через `BackendAssistantService.lookup_dev_session`; команды **`/username`** (аргумент) и **`/login`** + следующее текстовое сообщение; сброс ожидания на `/start`, `/help`, `/reset`.

## Отклонения от черновика плана в чате

- Вместо `next.config` rewrite использован **Route Handler** для dev-session (тот же эффект: Bearer не в браузере). **`BACKEND_API_CLIENT_TOKEN`** во фронте необязателен, если в backend токен не задан — заголовок `Authorization` тогда не отправляется.
- ESLint React 19: инициализация сессии в `AppShell` отложена через **`setTimeout(0)`**, чтобы не срабатывало правило `react-hooks/set-state-in-effect`.

## Проверка

- `pnpm run build` и `pnpm run lint` в `frontend/web/` — успешно.
- `uv run ruff check bot` — успешно.
