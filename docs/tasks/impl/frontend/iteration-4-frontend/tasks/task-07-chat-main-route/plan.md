# Задача 07: Чат в основной области (меню «Чат»)

## Цель

Отдельная страница «Чат» с полной историей и тем же диалоговым API, что и у плавающего виджета (задача 06).

## Источники

- [docs/tasks/tasklist-frontend.md](../../../../../../tasks/tasklist-frontend.md)
- [docs/tech/frontend-requirements.md](../../../../../../tech/frontend-requirements.md) §6.4
- [docs/tech/api-contracts.md](../../../../../../tech/api-contracts.md)

## Решение по `dialogue_id`

Один веб-диалог на сессию: `web_dialogue_id` в `localStorage` ([frontend/web/lib/session.ts](../../../../../../../frontend/web/lib/session.ts)), обновление через `patchWebSession` после ответа `POST .../dialogues/messages`.

Состояние переписки (`lines`, отправка, ошибки) — **один** экземпляр в `WebDialogueChatProvider` ([frontend/web/components/web-dialogue-chat-context.tsx](../../../../../../../frontend/web/components/web-dialogue-chat-context.tsx)), чтобы страница `/chat` и плавающая панель не расходились.

## Состав работ (факт реализации)

1. [frontend/web/components/web-session-context.tsx](../../../../../../../frontend/web/components/web-session-context.tsx) — `WebSessionProvider`, `useWebSession`.
2. [frontend/web/hooks/use-web-dialogue-chat.ts](../../../../../../../frontend/web/hooks/use-web-dialogue-chat.ts) — загрузка ходов, отправка, сброс, `fetchHistory()` для повторной подгрузки (открытие Sheet).
3. [frontend/web/components/chat-conversation-panel.tsx](../../../../../../../frontend/web/components/chat-conversation-panel.tsx) — терминальный UI списка и формы; локальная прокрутка вниз.
4. [frontend/web/components/chat-widget-shell.tsx](../../../../../../../frontend/web/components/chat-widget-shell.tsx) — FAB + Sheet, вызов общей панели и `fetchHistory` при открытии.
5. [frontend/web/components/app-shell.tsx](../../../../../../../frontend/web/components/app-shell.tsx) — провайдеры; для `pathname === "/chat"` у `main` отключены `p-6` и включены `flex min-h-0 flex-col overflow-hidden`.
6. [frontend/web/app/(app)/chat/page.tsx](../../../../../../../frontend/web/app/(app)/chat/page.tsx) — заголовок, сброс, панель переписки.

## Отложено

- Пагинация истории по `before_asked_at` (не MVP).
