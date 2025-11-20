"""Runner del bot de Telegram usando python-telegram-bot estilo tutorial."""
import json
import logging
import os
import re
from functools import wraps

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import TelegramError, BadRequest

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
        try:
            context.bot.send_message(chat_id, text.upper(), entities=message.entities)
            telegram_service.log_outgoing_message(chat_id, text.upper())
        except Exception as e:
            logger.error(f"Error en modo screaming: {e}")
            _send_safe_message(context, chat_id, text.upper(), telegram_service)
        return

    business_id = _get_active_business_id()
    if not business_id:
        _send_safe_message(context, chat_id, 'Aún no hay negocio activo configurado. Inténtalo más tarde.')
        return

    customer_identifier = _build_customer_identifier(message)
    ai_agent = AIAgentService()
    
    try:
        result = ai_agent.process_message(
            customer_phone=customer_identifier,
            message_text=text,
            business_id=business_id,
            channel='telegram'
        )

        # Log para debugging
        logger.info(f"Tipo de resultado: {type(result)}")
        logger.info(f"Resultado AI (primeros 200 chars): {str(result)[:200]}")
        
        # Asegurar que result sea un dict
        if isinstance(result, str):
            parsed = _try_parse_jsonish(result)
            if parsed:
                logger.info('Resultado string convertido a dict tras parseo adicional.')
                result = parsed
        
        if not isinstance(result, dict):
            logger.error(f"El resultado no es un diccionario: {result}")
            clean = _clean_ai_response_text(result)
            _send_safe_message(context, chat_id, clean or "Lo siento, hubo un problema procesando tu mensaje.", telegram_service)
            return

        response_text = _clean_ai_response_text(result.get('response'))
        logger.info(f"Texto de respuesta extraído: {response_text[:100]}")
        
        if response_text:
            _send_safe_message(context, chat_id, response_text, telegram_service)
        
        # No enviar mensaje duplicado de missing_info si ya está en la respuesta
        if result.get('needs_more_info') and result.get('missing_info_message'):
            missing_msg = result.get('missing_info_message', '')
            # Solo enviar si no está ya incluido en response_text
            if missing_msg and missing_msg not in response_text:
                _send_safe_message(context, chat_id, missing_msg, telegram_service)
                
    except Exception as e:
        logger.error(f"Error procesando mensaje con AI: {e}", exc_info=True)
        _send_safe_message(context, chat_id, "Lo siento, hubo un error procesando tu solicitud. Por favor intenta nuevamente.", telegram_service)


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


def _strip_code_fences(text):
    """Elimina delimitadores ``` opcionales alrededor del contenido."""
    if not isinstance(text, str):
        return text
    stripped = text.strip()
    match = re.match(r"^```(?:[a-zA-Z0-9_-]+)?\s*(.*?)\s*```$", stripped, re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def _try_parse_jsonish(text):
    """Intenta parsear un string que aparenta ser JSON aunque tenga ruido."""
    if not text:
        return None
    cleaned = _strip_code_fences(text)
    # Remover trailing texto después de último cierre }
    if '}' in cleaned:
        cleaned = cleaned[:cleaned.rfind('}') + 1]
    # Buscar primer bloque JSON delimitado por llaves
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    candidate = match.group(0) if match else cleaned
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _clean_ai_response_text(raw_text):
    """Devuelve un texto legible a partir del campo response."""
    if raw_text is None:
        return ''

    if isinstance(raw_text, dict):
        nested = raw_text.get('response') or raw_text.get('message') or raw_text.get('text')
        if nested:
            return _clean_ai_response_text(nested)
        # Como último recurso, concatenar valores simples
        pieces = [f"{k}: {v}" for k, v in raw_text.items() if isinstance(v, (str, int, float))]
        return '\n'.join(pieces)

    if isinstance(raw_text, list):
        return '\n'.join(str(item) for item in raw_text if item)

    text = _strip_code_fences(str(raw_text))

    if text.startswith('{') or '"response"' in text:
        parsed = _try_parse_jsonish(text)
        if isinstance(parsed, dict):
            nested = parsed.get('response') or parsed.get('message') or parsed.get('text')
            if nested:
                return _clean_ai_response_text(nested)
        if parsed is not None:
            # No encontramos campo específico pero había JSON válido
            return '\n'.join(f"{k}: {v}" for k, v in parsed.items()) if isinstance(parsed, dict) else str(parsed)

    return text


def _escape_markdown(text):
    """Escapa caracteres especiales de Markdown V1."""
    if not text:
        return text
    # Caracteres especiales de Markdown que necesitan ser escapados
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def _send_safe_message(context, chat_id, text, telegram_service=None):
    """Envía un mensaje de forma segura, intentando con Markdown y fallback a texto plano."""
    try:
        # Primero intenta sin parse_mode (texto plano)
        context.bot.send_message(chat_id, text)
        if telegram_service:
            telegram_service.log_outgoing_message(chat_id, text)
        return True
    except BadRequest as e:
        logger.error(f"Error enviando mensaje: {e}")
        # Si falla, intenta con un mensaje genérico
        try:
            context.bot.send_message(chat_id, "Lo siento, hubo un problema procesando tu solicitud. Por favor, intenta nuevamente.")
            if telegram_service:
                telegram_service.log_outgoing_message(chat_id, "Error en el mensaje")
        except Exception as ex:
            logger.error(f"Error crítico enviando mensaje de fallback: {ex}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado enviando mensaje: {e}")
        return False


def error_handler(update: Update, context: CallbackContext):
    """Maneja errores globales del bot."""
    logger.error(f'Error en actualización {update}: {context.error}')
    
    # Intenta notificar al usuario si es posible
    if update and update.effective_chat:
        try:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Lo siento, ocurrió un error procesando tu mensaje. Por favor intenta nuevamente."
            )
        except Exception as e:
            logger.error(f'Error enviando mensaje de error al usuario: {e}')


def main():
    with flask_app.app_context():
        token = flask_app.config.get('TELEGRAM_BOT_TOKEN')
        if not token:
            raise RuntimeError('TELEGRAM_BOT_TOKEN no configurado')

        updater = Updater(token)
        dispatcher = updater.dispatcher

        # Agregar handlers
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('scream', scream))
        dispatcher.add_handler(CommandHandler('whisper', whisper))
        dispatcher.add_handler(CommandHandler('menu', menu))
        dispatcher.add_handler(CallbackQueryHandler(button_tap))
        dispatcher.add_handler(MessageHandler(~Filters.command, echo))
        
        # Agregar error handler global
        dispatcher.add_error_handler(error_handler)

        logger.info('Bot de Telegram iniciado. Presiona Ctrl+C para detenerlo.')
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
