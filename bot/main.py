import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import Config
from bot.handlers.command_handler import build_command_router
from bot.handlers.message_handler import build_message_router
from bot.services.llm_service import LlmService
from bot.utils.logger import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    config = Config()
    setup_logging(config.log_level)

    prompt_path = config.resolved_system_prompt_path()
    if not prompt_path.is_file():
        msg = (
            f"Файл системного промпта не найден: {prompt_path.resolve()}. "
            "Проверьте SYSTEM_PROMPT_PATH в .env"
        )
        raise FileNotFoundError(msg)

    system_prompt = prompt_path.read_text(encoding="utf-8")
    llm = LlmService(config, system_prompt)

    bot = Bot(token=config.telegram_token)
    dp = Dispatcher()
    dp.include_router(build_command_router(llm))
    dp.include_router(build_message_router(llm))

    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
