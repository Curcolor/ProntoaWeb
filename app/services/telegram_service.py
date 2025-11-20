"""
Servicio de integración provisional con Telegram Bot API.
Permite enviar y recibir mensajes vía BotFather para pruebas.
"""
from __future__ import annotations

import requests
from flask import current_app
from app.extensions import db
from app.data.models import Message, Order


class TelegramService:
    """Servicio utilitario para interactuar con Telegram Bot API."""

    def __init__(self):
        self.bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    @property
    def configured(self) -> bool:
        return bool(self.bot_token and self.base_url)

    def send_message(self, chat_id, text, order_id=None, parse_mode='Markdown'):
        """Envía un mensaje simple al chat indicado."""
        if not self.configured:
            current_app.logger.warning('TelegramService: bot token no configurado')
            return False, None

        try:
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('result', {}).get('message_id')
                self._save_message(
                    telegram_message_id=f"tg_{message_id}",
                    sender='telegram_bot',
                    receiver=str(chat_id),
                    content=text,
                    direction='outbound',
                    is_automated=True,
                    order_id=order_id
                )
                return True, message_id

            current_app.logger.error(f"TelegramService: error enviando mensaje {response.text}")
            return False, None
        except Exception as exc:
            current_app.logger.error(f"TelegramService: excepción en send_message {exc}")
            return False, None

    def send_order_confirmation(self, order: Order):
        chat_id = self._get_customer_identifier(order)
        if not chat_id:
            return False

        items_text = "\n".join([
            f"• {item.product_name} x{item.quantity} - ${item.subtotal:,.0f}"
            for item in order.items
        ])
        message = f"""
*Pedido #{order.order_number}* confirmado ✅\n\n{items_text}\n\nTotal: ${order.total_amount:,.0f}\nTipo: {order.order_type}\n{f'Dirección: {order.delivery_address}' if order.delivery_address else ''}\n\nGracias por pedir con ProntoaWeb.
""".strip()
        success, _ = self.send_message(chat_id, message)
        return success

    def send_order_ready(self, order: Order):
        chat_id = self._get_customer_identifier(order)
        if not chat_id:
            return False
        status_line = 'Tu pedido va en camino 🚚' if order.order_type == 'delivery' else 'Puedes recogerlo cuando gustes 🏪'
        message = f"""
Pedido #{order.order_number} listo ✅\n\n{status_line}
""".strip()
        success, _ = self.send_message(chat_id, message)
        return success

    def send_order_delivered(self, order: Order):
        chat_id = self._get_customer_identifier(order)
        if not chat_id:
            return False
        message = f"""
Pedido #{order.order_number} entregado 🎉\n\nCuéntanos cómo estuvo todo. ¡Gracias por preferirnos!
""".strip()
        success, _ = self.send_message(chat_id, message)
        return success

    def process_incoming_message(self, update):
        """Persiste un mensaje entrante para trazabilidad."""
        try:
            message = update.get('message') or {}
            if not message:
                return

            message_id = message.get('message_id')
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text')
            username = message.get('from', {}).get('username')
            sender_identifier = self._build_sender_identifier(chat_id, username)

            self._save_message(
                telegram_message_id=f"tg_{message_id}",
                sender=sender_identifier,
                receiver='telegram_bot',
                content=text,
                direction='inbound',
                is_automated=False
            )
        except Exception as exc:
            current_app.logger.error(f"TelegramService: no se pudo registrar mensaje entrante {exc}")

    def _save_message(self, telegram_message_id, sender, receiver, content, direction, is_automated, order_id=None):
        try:
            message = Message(
                whatsapp_message_id=telegram_message_id,
                sender_phone=self._sanitize_identifier(sender),
                receiver_phone=self._sanitize_identifier(receiver),
                content=content,
                direction=direction,
                is_automated=is_automated,
                order_id=order_id,
                status='sent'
            )
            db.session.add(message)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error(f"TelegramService: error guardando mensaje {exc}")

    def _get_customer_identifier(self, order: Order):
        if order and order.customer and order.customer.phone:
            stored = order.customer.phone
            if stored.startswith('tg:'):
                return stored.split(':', 1)[1]
            return stored
        return None

    @staticmethod
    def _build_sender_identifier(chat_id, username):
        if username:
            return f"tg:{username}"
        return f"tg:{chat_id}"

    @staticmethod
    def _sanitize_identifier(value):
        if value is None:
            return None
        return str(value)[:20]
