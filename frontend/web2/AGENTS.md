<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Репозиторий LLMStart

- Продукт и границы: [docs/vision.md](../../docs/vision.md)
- Обзор системы: [docs/architecture.md](../../docs/architecture.md)
- HTTP v1 (сводка): [docs/tech/api-contracts.md](../../docs/tech/api-contracts.md)
- Онбординг и команды: [docs/onboarding.md](../../docs/onboarding.md), корневой [README.md](../../README.md)
- Шаблоны env: [backend/.env.example](../../backend/.env.example), [bot/.env.example](../../bot/.env.example), [frontend/web/.env.example](.env.example) → локально **`.env.local`**
- Проверки: `pnpm lint`, `pnpm build`; из корня также `make ci-check` / `.\tasks.ps1 ci-check` (вместе с ruff по Python)
