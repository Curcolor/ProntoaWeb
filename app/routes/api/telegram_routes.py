"""
Blueprint de integración provisional con Telegram Bot API.
Permite recibir mensajes desde un chatbot de BotFather y responder usando la IA existente.
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required
from app.services.telegram_service import TelegramService
from app.services.ai_service import AIAgentService

telegram_api_bp = Blueprint('telegram_api', __name__, url_prefix='/api/telegram')


@telegram_api_bp.route('/webhook/<secret>', methods=['POST'])
def telegram_webhook(secret):
    """Endpoint que recibe actualizaciones de Telegram."""
    expected_secret = current_app.config.get('TELEGRAM_WEBHOOK_SECRET')
    if expected_secret and secret != expected_secret:
        return jsonify({'success': False, 'message': 'Forbidden'}), 403

    update = request.get_json(silent=True) or {}
    telegram_service = TelegramService()

    if not telegram_service.configured:
        current_app.logger.warning('Telegram webhook recibido sin bot token configurado')
        return jsonify({'success': False, 'message': 'Telegram no configurado'}), 503

    message = update.get('message')
    if not message:
        return jsonify({'success': True}), 200

    chat = message.get('chat', {})
    chat_id = chat.get('id')
    text = message.get('text') or ''

    if not chat_id or not text.strip():
        return jsonify({'success': True}), 200

    telegram_service.process_incoming_message(update)

    business_id = _get_active_business_id()
    if not business_id:
        current_app.logger.warning('Telegram webhook: no hay negocios activos configurados')
        return jsonify({'success': True}), 200

    customer_identifier = _build_customer_identifier(message)
    ai_agent = AIAgentService()
    ai_result = ai_agent.process_message(
        customer_phone=customer_identifier,
        message_text=text,
        business_id=business_id,
        channel='telegram'
    )

    response_text = ai_result.get('response')
    if response_text:
        telegram_service.send_message(chat_id, response_text)

    return jsonify({'success': True}), 200


@telegram_api_bp.route('/send', methods=['POST'])
@login_required
def send_telegram_message():
    data = request.get_json() or {}
    chat_id = data.get('chat_id') or data.get('customer_identifier')
    text = data.get('message')

    if not chat_id or not text:
        return jsonify({'success': False, 'message': 'chat_id y message son requeridos'}), 400

    telegram_service = TelegramService()
    success, message_id = telegram_service.send_message(chat_id, text)

    if success:
        return jsonify({'success': True, 'message_id': message_id}), 200
    return jsonify({'success': False, 'message': 'Error enviando mensaje'}), 500


def _get_active_business_id():
    try:
        from app.data.models import Business
        business = Business.query.filter_by(is_active=True).first()
        return business.id if business else None
    except Exception as exc:
        current_app.logger.error(f'Telegram webhook: error obteniendo negocio activo {exc}')
        return None


def _build_customer_identifier(message):
    user = message.get('from', {})
    phone = user.get('phone_number')
    if phone:
        return phone

    chat_id = message.get('chat', {}).get('id')
    if chat_id:
        return f"tg:{chat_id}"

    username = user.get('username')
    if username:
        return f"tg:{username}"

    return 'tg:unknown'
