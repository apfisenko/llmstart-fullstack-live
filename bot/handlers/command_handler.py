import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.backend_assistant import BackendAssistantService
from bot.utils.logger import hash_chat_id

logger = logging.getLogger(__name__)

WELCOME = (
    "Привет! Я бот-помощник курса AI-driven fullstack developer.\n\n"
    "Отвечаю на вопросы по программе, расписанию и навигации по материалам. "
    "Пиши вопрос текстом.\n\n"
    "Команды:\n"
    "/help — это сообщение\n"
    "/reset — сбросить историю диалога"
)


def build_command_router(llm: BackendAssistantService) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        if message.chat is None:
            return
        ch = hash_chat_id(message.chat.id)
        logger.info("command start chat_hash=%s", ch)
        await message.answer(WELCOME)

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        if message.chat is None:
            return
        ch = hash_chat_id(message.chat.id)
        logger.info("command help chat_hash=%s", ch)
        await message.answer(WELCOME)

    @router.message(Command("reset"))
    async def cmd_reset(message: Message) -> None:
        if message.chat is None:
            return
        ch = hash_chat_id(message.chat.id)
        logger.warning("history reset chat_hash=%s", ch)
        await llm.reset_history(message.chat.id)
        await message.answer("История диалога сброшена.")

    return router
