import logging

from aiogram import F, Router
from aiogram.enums import ChatAction, ChatType
from aiogram.types import Message

from bot.services.backend_assistant import BackendAssistantService
from bot.utils.logger import hash_chat_id

logger = logging.getLogger(__name__)


def build_message_router(llm: BackendAssistantService) -> Router:
    router = Router()

    @router.message(F.text & ~F.text.startswith("/"))
    async def handle_text(message: Message) -> None:
        if message.chat is None or message.text is None:
            return
        if message.chat.type != ChatType.PRIVATE:
            ch = hash_chat_id(message.chat.id)
            logger.warning(
                "text ignored non-private chat chat_hash=%s chat_type=%s",
                ch,
                message.chat.type,
            )
            await message.answer(
                "Отвечаю только в личном чате. В группах Telegram по умолчанию "
                "не передаёт боту обычные сообщения — откройте диалог со мной напрямую "
                "(иконка бота → «Сообщение»)."
            )
            return
        chat_id = message.chat.id
        ch = hash_chat_id(chat_id)
        text = message.text
        logger.info("message text chat_hash=%s len=%s", ch, len(text))
        try:
            await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            reply = await llm.chat(chat_id, text)
            await message.answer(reply)
            logger.info("reply sent chat_hash=%s len=%s", ch, len(reply))
        except Exception as exc:
            logger.exception("handle_text failed chat_hash=%s", ch)
            err_name = type(exc).__name__
            if "Proxy" in err_name and "Timeout" in err_name:
                fallback = (
                    "Таймаут подключения к прокси для Telegram. Проверьте PROXY_URL в .env "
                    "или оставьте переменную пустой, если прокси не нужен."
                )
            elif "Proxy" in err_name:
                fallback = (
                    "Ошибка прокси для Telegram. Проверьте PROXY_URL в .env или отключите прокси."
                )
            else:
                fallback = "Произошла ошибка при обработке сообщения. Попробуйте позже."
            try:
                await message.answer(fallback)
            except Exception:
                logger.exception(
                    "failed to send error reply (check PROXY_URL if using proxy) chat_hash=%s",
                    ch,
                )

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
