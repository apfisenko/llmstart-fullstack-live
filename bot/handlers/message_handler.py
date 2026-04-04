import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from bot.services.llm_service import LlmService
from bot.utils.logger import hash_chat_id

logger = logging.getLogger(__name__)


def build_message_router(llm: LlmService) -> Router:
    router = Router()

    @router.message(F.text & ~F.text.startswith("/"))
    async def handle_text(message: Message) -> None:
        if message.chat is None or message.text is None:
            return
        chat_id = message.chat.id
        ch = hash_chat_id(chat_id)
        text = message.text
        logger.info("message text chat_hash=%s len=%s", ch, len(text))
        await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        reply = await llm.chat(chat_id, text)
        await message.answer(reply)
        logger.info("reply sent chat_hash=%s len=%s", ch, len(reply))

    @router.message(~F.text)
    async def handle_non_text(message: Message) -> None:
        if message.chat is None:
            return
        ch = hash_chat_id(message.chat.id)
        logger.warning(
            "non-text message chat_hash=%s content_type=%s",
            ch,
            message.content_type,
        )
        await message.answer("Работаю только с текстовыми сообщениями.")

    return router
