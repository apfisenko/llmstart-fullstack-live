# Задача 06: Глобальный чат — итог

## Сделано

- Прокси к backend: [`frontend/web/app/api/v1/cohorts/[cohort_id]/dialogues/messages/route.ts`](../../../../../../../frontend/web/app/api/v1/cohorts/[cohort_id]/dialogues/messages/route.ts) (POST), [`frontend/web/app/api/v1/dialogues/[dialogue_id]/turns/route.ts`](../../../../../../../frontend/web/app/api/v1/dialogues/[dialogue_id]/turns/route.ts) (GET), [`frontend/web/app/api/v1/dialogues/[dialogue_id]/reset/route.ts`](../../../../../../../frontend/web/app/api/v1/dialogues/[dialogue_id]/reset/route.ts) (POST)
- Типы и `parseApiErrorMessage`: [`frontend/web/lib/dialogue-api.ts`](../../../../../../../frontend/web/lib/dialogue-api.ts)
- Частичное обновление сессии: [`frontend/web/lib/session.ts`](../../../../../../../frontend/web/lib/session.ts) — `patchWebSession`
- Виджет: [`frontend/web/components/chat-widget-shell.tsx`](../../../../../../../frontend/web/components/chat-widget-shell.tsx) — терминальный UI (ассистент слева с иконкой, пользователь справа), история при открытии (`limit=50`), `AbortController` при перезагрузке истории, индикатор отправки, обработка 502/503 без сырого текста LLM
- Подключение в shell: [`frontend/web/components/app-shell.tsx`](../../../../../../../frontend/web/components/app-shell.tsx) — `session` и `onSessionChange`

## Отклонения / ограничения MVP

- Подгрузка более старых ходов при скролле вверх (`next_before_asked_at`) не реализована — только первая страница истории
- Ответ ассистента только целиком из JSON (без streaming), в соответствии с OpenAPI

## Проверка

- `pnpm lint`, `pnpm exec tsc --noEmit` в `frontend/web/`
- Ручная: backend + `pnpm dev` — FAB → сообщение → ответ; кнопка «Сброс» очищает историю в панели
