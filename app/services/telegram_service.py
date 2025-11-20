"""Utilidades para registrar mensajes de Telegram en base de datos."""
from __future__ import annotations

from flask import current_app
from app.extensions import db
from app.data.models import Message, Order


class TelegramService:
    """Persistencia y utilidades para la integración de Telegram."""

    def __init__(self):
        self.bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

    def log_incoming_message(self, update_dict):
        """Guarda mensajes entrantes provenientes de un Update del bot."""
        try:
            message = (update_dict or {}).get('message') or {}
            if not message:
                return

            message_id = message.get('message_id')
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text')
            username = message.get('from', {}).get('username')

            self._save_message(
                telegram_message_id=self._format_message_id(message_id),
                sender=self._build_sender_identifier(chat_id, username),
                receiver='telegram_bot',
                content=text,
                direction='inbound',
                is_automated=False
            )
        except Exception as exc:
            current_app.logger.error(f"TelegramService: no se pudo registrar mensaje entrante {exc}")

    def log_outgoing_message(self, chat_id, text, order_id=None, sender='telegram_bot'):
        """Registra un mensaje enviado al usuario (aunque se envíe desde otro proceso)."""
        try:
            self._save_message(
                telegram_message_id=None,
                sender=self._sanitize_identifier(sender),
                receiver=self._sanitize_identifier(chat_id),
                content=text,
                direction='outbound',
                is_automated=True,
                order_id=order_id
            )
        except Exception as exc:
            current_app.logger.error(f"TelegramService: no se pudo registrar mensaje saliente {exc}")

    def attach_order_identifier(self, order: Order, chat_id: str):
        """Asocia el identificador tg: al teléfono del cliente si aún no existe."""
        try:
            if not order or not order.customer:
                return
            normalized = self._normalize_chat_identifier(chat_id)
            if not normalized:
                return
            if not order.customer.phone or not order.customer.phone.startswith('tg:'):
                order.customer.phone = normalized
                db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error(f"TelegramService: no se pudo asociar cliente {exc}")

    def send_order_status_update(self, order: Order, new_status: str):
        chat_id = self._extract_chat_id(order)
        if not chat_id or not self.base_url:
            return False

        message = self._build_status_message(order, new_status)
        if not message:
            return False

        sent = self._send_bot_message(chat_id, message)
        if sent:
            self.log_outgoing_message(chat_id, message, order_id=order.id)
        return sent

    def _send_bot_message(self, chat_id, text):
        if not self.base_url:
            current_app.logger.warning('TelegramService: bot token no configurado, no se envía status update')
            return False
        try:
            import requests  # type: ignore
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'},
                timeout=10
            )
            if response.status_code != 200:
                current_app.logger.error(f"TelegramService: error enviando mensaje {response.text}")
                return False
            return True
        except Exception as exc:
            current_app.logger.error(f"TelegramService: excepción enviando mensaje {exc}")
            return False

    def _extract_chat_id(self, order: Order):
        if not order or not order.customer or not order.customer.phone:
            return None
        phone = order.customer.phone
        if phone.startswith('tg:'):
            identifier = phone.split(':', 1)[1]
            if identifier.isdigit():
                return int(identifier)
        return None

    def _build_status_message(self, order: Order, new_status: str):
        if not order:
            return None
        templates = {
            'preparing': f"Tu pedido #{order.order_number} está en preparación 👩‍🍳",
            'ready': self._ready_message(order),
            'sent': self._sent_message(order),
            'out_for_delivery': self._sent_message(order),
            'paid': f"¡Gracias! Pedido #{order.order_number} fue marcado como pagado ✅",
            'delivered': f"Pedido #{order.order_number} fue entregado. ¡Disfrútalo!"
        }
        return templates.get(new_status)

    def _ready_message(self, order: Order):
        if order.order_type == 'pickup':
            return f"Pedido #{order.order_number} está listo para recoger en tienda."
        return f"Pedido #{order.order_number} está listo y saldrá en breve hacia tu dirección."

    def _sent_message(self, order: Order):
        if order.order_type == 'pickup':
            return f"Pedido #{order.order_number} fue entregado al repartidor para retiro coordinado."
        return f"Pedido #{order.order_number} ya va en camino 🚚"

    @staticmethod
    def _format_message_id(message_id):
        return f"tg_{message_id}" if message_id else None

    @staticmethod
    def _build_sender_identifier(chat_id, username):
        if username:
            return f"tg:{username}"
        if chat_id:
            return f"tg:{chat_id}"
        return 'tg:unknown'

    @staticmethod
    def _normalize_chat_identifier(chat_id):
        if chat_id is None:
            return None
        return f"tg:{chat_id}"

    @staticmethod
    def _sanitize_identifier(value):
        if value is None:
            return None
        return str(value)[:32]

    def _save_message(self, telegram_message_id, sender, receiver, content, direction, is_automated, order_id=None):
        if not content and direction == 'outbound':
            content = '[mensaje vacío]'

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
        try:
            db.session.add(message)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error(f"TelegramService: error guardando mensaje {exc}")
