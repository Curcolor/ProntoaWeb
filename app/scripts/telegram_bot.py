"""Runner del bot de Telegram usando python-telegram-bot estilo tutorial."""
import logging
import os
from functools import wraps

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

from app import create_app
from app.services.ai_service import AIAgentService
from app.services.telegram_service import TelegramService
from app.data.models import Business

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Estado global (imitando el tutorial)
screaming = False

FIRST_MENU = "<b>Menú principal</b>\n\nBot experimental de pedidos ProntoaWeb."
SECOND_MENU = "<b>Ayuda</b>\n\n1. Escribe tu pedido\n2. Indica si lo quieres delivery o pickup\n3. Comparte dirección si es delivery"
NEXT_BUTTON = "Ver ayuda"
BACK_BUTTON = "Volver"
TUTORIAL_BUTTON = "Docs Telegram"
FIRST_MENU_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
])

# Crear app Flask para reutilizar servicios
flask_app = create_app(os.getenv('FLASK_CONFIG'))


def with_app_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with flask_app.app_context():
            return func(*args, **kwargs)
    return wrapper


@with_app_context
def start(update: Update, context: CallbackContext):
    """Comando /start clásico."""
    user = update.effective_user
    telegram_service = TelegramService()
    telegram_service.log_incoming_message(update.to_dict())
    update.message.reply_text(
        f"Hola {user.first_name}! Soy tu bot de pedidos de ProntoaWeb. 🤖\nPuedes escribirme lo que deseas ordenar.",
        reply_markup=ForceReply(selective=True)
    )


@with_app_context
def scream(update: Update, context: CallbackContext):
    global screaming
    screaming = True
    update.message.reply_text("Screaming mode ON 🔊")


@with_app_context
def whisper(update: Update, context: CallbackContext):
    global screaming
    screaming = False
    update.message.reply_text("Screaming mode OFF 🤫")


@with_app_context
def menu(update: Update, context: CallbackContext):
    update.message.reply_text(
        FIRST_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )


@with_app_context
def button_tap(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    text = FIRST_MENU
    markup = FIRST_MENU_MARKUP

    if data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP

    query.answer()
    query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)


@with_app_context
def echo(update: Update, context: CallbackContext):
    """Handler de mensajes inspirado en el tutorial, pero conectado al agente IA."""
    global screaming
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    chat_id = message.chat_id
    telegram_service = TelegramService()
    telegram_service.log_incoming_message(update.to_dict())

    if screaming:
        context.bot.send_message(chat_id, text.upper(), entities=message.entities)
        telegram_service.log_outgoing_message(chat_id, text.upper())
        return

    business_id = _get_active_business_id()
    if not business_id:
        context.bot.send_message(chat_id, 'Aún no hay negocio activo configurado. Inténtalo más tarde.')
        return

    customer_identifier = _build_customer_identifier(message)
    ai_agent = AIAgentService()
    result = ai_agent.process_message(
        customer_phone=customer_identifier,
        message_text=text,
        business_id=business_id,
        channel='telegram'
    )

    response_text = result.get('response')
    if response_text:
        context.bot.send_message(chat_id, response_text, parse_mode=ParseMode.MARKDOWN)
        telegram_service.log_outgoing_message(chat_id, response_text)

    if result.get('needs_more_info') and result.get('missing_info'):
        friendly = result.get('missing_info_message') or 'Necesito algunos datos adicionales para continuar con tu pedido.'
        context.bot.send_message(chat_id, friendly)
        telegram_service.log_outgoing_message(chat_id, friendly)


def _get_active_business_id():
    business = Business.query.filter_by(is_active=True).first()
    return business.id if business else None


def _build_customer_identifier(message):
    user = message.from_user or {}
    phone = getattr(user, 'phone_number', None)
    if phone:
        return phone
    chat_id = message.chat_id
    username = user.username
    if username:
        return f"tg:{username}"
    return f"tg:{chat_id}"


def main():
    with flask_app.app_context():
        token = flask_app.config.get('TELEGRAM_BOT_TOKEN')
        if not token:
            raise RuntimeError('TELEGRAM_BOT_TOKEN no configurado')

        updater = Updater(token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('scream', scream))
        dispatcher.add_handler(CommandHandler('whisper', whisper))
        dispatcher.add_handler(CommandHandler('menu', menu))
        dispatcher.add_handler(CallbackQueryHandler(button_tap))
        dispatcher.add_handler(MessageHandler(~Filters.command, echo))

        logger.info('Bot de Telegram iniciado. Presiona Ctrl+C para detenerlo.')
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
