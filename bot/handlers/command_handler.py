import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.services.backend_assistant import BackendAssistantService
from bot.state.pending_dev_username import clear_waiting_username, mark_waiting_username
from bot.utils.logger import hash_chat_id

logger = logging.getLogger(__name__)

WELCOME = (
    "Привет! Я бот-помощник курса AI-driven fullstack developer.\n\n"
    "Отвечаю на вопросы по программе, расписанию и навигации по материалам. "
    "Пиши вопрос текстом.\n\n"
    "Проверка username для веб-входа (тот же API, что и в браузере):\n"
    "/username имя — запрос к backend (без пробелов в имени)\n"
    "/login — бот попросит ввести username следующим сообщением\n\n"
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
        clear_waiting_username(message.chat.id)
        ch = hash_chat_id(message.chat.id)
        logger.info("command start chat_hash=%s", ch)
        await message.answer(WELCOME)

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        if message.chat is None:
            return
        clear_waiting_username(message.chat.id)
        ch = hash_chat_id(message.chat.id)
        logger.info("command help chat_hash=%s", ch)
        await message.answer(WELCOME)

    @router.message(Command("reset"))
    async def cmd_reset(message: Message) -> None:
        if message.chat is None:
            return
        clear_waiting_username(message.chat.id)
        ch = hash_chat_id(message.chat.id)
        logger.warning("history reset chat_hash=%s", ch)
        await llm.reset_history(message.chat.id)
        await message.answer("История диалога сброшена.")

    @router.message(Command("login"))
    async def cmd_login(message: Message) -> None:
        if message.chat is None:
            return
        mark_waiting_username(message.chat.id)
        ch = hash_chat_id(message.chat.id)
        logger.info("command login prompt chat_hash=%s", ch)
        await message.answer(
            "Введите Telegram username следующим сообщением (без @, одной строкой). "
            "Отмена: /start или /reset."
        )

    @router.message(Command("username"))
    async def cmd_username(message: Message, command: CommandObject) -> None:
        if message.chat is None:
            return
        ch = hash_chat_id(message.chat.id)
        arg = (command.args or "").strip()
        if not arg:
            await message.answer("Использование: /username имя_или_@имя")
            return
        logger.info("command username chat_hash=%s arg_len=%s", ch, len(arg))
        text = await llm.lookup_dev_session(arg, ch)
        await message.answer(text)

    return router
