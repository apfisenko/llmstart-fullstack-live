import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (
    TelegramConflictError,
    TelegramNetworkError,
    TelegramUnauthorizedError,
)

from bot.config import Config
from bot.handlers.command_handler import build_command_router
from bot.handlers.message_handler import build_message_router
from bot.services.backend_assistant import BackendAssistantService
from bot.utils.logger import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    config = Config()
    setup_logging(config.log_level)

    assistant = BackendAssistantService(config)
    try:
        if config.proxy_url.strip():
            logger.warning(
                "PROXY_URL задан — все запросы бота к Telegram API идут через прокси; "
                "при таймаутах очистите переменную в bot/.env, если прокси не нужен."
            )
        session = AiohttpSession(
            proxy=config.proxy_url or None,
            timeout=float(config.telegram_request_timeout),
        )
        bot = Bot(token=config.telegram_token, session=session)
        dp = Dispatcher()
        dp.include_router(build_command_router(assistant))
        dp.include_router(build_message_router(assistant))

        if config.cohort_id is None or config.membership_id is None:
            logger.warning(
                "COHORT_ID/MEMBERSHIP_ID не заданы — guest-режим LLM "
                "(POST /api/v1/assistant/guest/*)."
            )
        logger.info("Bot started backend_base=%s", config.resolved_backend_base_url())
        # Иначе при включённом webhook long polling не получает апдейты
        # (в логах только Start polling).
        await bot.delete_webhook(drop_pending_updates=False)
        logger.info("Telegram webhook cleared; using long polling")

        while True:
            try:
                await dp.start_polling(bot)
                break
            except TelegramUnauthorizedError:
                logger.critical(
                    "Telegram отклонил TELEGRAM_TOKEN (401). Проверьте токен; "
                    "убедитесь, что в bot/.env нет лишних пробелов или CRLF в конце строки."
                )
                raise
            except TelegramConflictError:
                logger.critical(
                    "TelegramConflictError: с этим токеном уже идёт long polling "
                    "в другом процессе. Остановите локальный бот (например .\\tasks.ps1 bot-dev), "
                    "другой контейнер или второй инстанс в другом окружении — "
                    "иначе контейнер будет уходить в restart."
                )
                raise
            except TelegramNetworkError as exc:
                logger.warning(
                    "TelegramNetworkError (доступ к api.telegram.org): %s. Повтор через 10 с. "
                    "При постоянных сбоях из Docker: прокси на хосте → "
                    "PROXY_URL=http://host.docker.internal:<порт> в bot/.env "
                    "(см. bot/.env.example).",
                    exc,
                )
                await asyncio.sleep(10)
    finally:
        await assistant.aclose()


if __name__ == "__main__":
    asyncio.run(main())
