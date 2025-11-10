"""
Servicio de integración con WhatsApp Business API.
Maneja envío y recepción de mensajes vía WhatsApp.
"""
import requests
import os
from flask import current_app
from app.extensions import db
from app.data.models import Message, Order


class WhatsAppService:
    """Servicio para integración con WhatsApp."""
    
    def __init__(self):
        self.api_key = current_app.config.get('WHATSAPP_API_KEY')
        self.phone_number_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        
    def send_message(self, to_phone, message_text, order_id=None):
        """
        Envía un mensaje de WhatsApp.
        
        Args:
            to_phone: Número de teléfono del destinatario
            message_text: Texto del mensaje
            order_id: ID del pedido relacionado (opcional)
            
        Returns:
            tuple: (success: bool, message_id: str or None)
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': 'text',
                'text': {
                    'body': message_text
                }
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                message_id = data['messages'][0]['id']
                
                # Guardar mensaje en base de datos
                self._save_message(
                    whatsapp_message_id=message_id,
                    sender_phone=self.phone_number_id,
                    receiver_phone=to_phone,
                    content=message_text,
                    direction='outbound',
                    is_automated=True,
                    order_id=order_id
                )
                
                return True, message_id
            else:
                current_app.logger.error(f"Error enviando WhatsApp: {response.text}")
                return False, None
                
        except Exception as e:
            current_app.logger.error(f"Excepción en send_message: {str(e)}")
            return False, None
    
    def send_order_confirmation(self, order):
        """
        Envía confirmación de pedido.
        
        Args:
            order: Objeto Order
            
        Returns:
            bool: Success
        """
        customer_phone = order.customer.phone
        
        items_text = "\n".join([
            f"• {item.product_name} x{item.quantity} - ${item.subtotal:,.0f}"
            for item in order.items
        ])
        
        message = f"""
¡Hola! 👋

Tu pedido ha sido recibido exitosamente.

*Pedido #{order.order_number}*

*Productos:*
{items_text}

*Total: ${order.total_amount:,.0f}*

Tipo: {order.order_type}
{f'Dirección: {order.delivery_address}' if order.delivery_address else ''}

Estamos preparando tu pedido y te notificaremos cuando esté listo. 

¡Gracias por tu compra! 🎉

_Mensaje automático de ProntoaWeb_
        """.strip()
        
        success, _ = self.send_message(customer_phone, message, order.id)
        return success
    
    def send_order_ready(self, order):
        """
        Envía notificación de pedido listo.
        
        Args:
            order: Objeto Order
            
        Returns:
            bool: Success
        """
        customer_phone = order.customer.phone
        
        message = f"""
¡Tu pedido está listo! ✅

*Pedido #{order.order_number}*

{'Tu pedido está en camino 🚚' if order.order_type == 'delivery' else 'Puedes pasar a recogerlo 🏪'}

¡Gracias por tu preferencia!

_Mensaje automático de ProntoaWeb_
        """.strip()
        
        success, _ = self.send_message(customer_phone, message, order.id)
        return success
    
    def send_order_delivered(self, order):
        """
        Envía notificación de pedido entregado.
        
        Args:
            order: Objeto Order
            
        Returns:
            bool: Success
        """
        customer_phone = order.customer.phone
        
        message = f"""
¡Pedido entregado! 🎉

*Pedido #{order.order_number}*

Esperamos que disfrutes tu pedido. 

¿Cómo fue tu experiencia? Tu opinión es muy importante para nosotros.

¡Hasta pronto! 😊

_Mensaje automático de ProntoaWeb_
        """.strip()
        
        success, _ = self.send_message(customer_phone, message, order.id)
        return success
    
    def process_incoming_message(self, message_data):
        """
        Procesa un mensaje entrante de WhatsApp.
        
        Args:
            message_data: Datos del webhook
            
        Returns:
            bool: Success
        """
        try:
            # Extraer información del mensaje
            message_id = message_data.get('id')
            from_phone = message_data.get('from')
            message_type = message_data.get('type')
            
            content = None
            media_url = None
            
            if message_type == 'text':
                content = message_data.get('text', {}).get('body')
            elif message_type == 'image':
                media_url = message_data.get('image', {}).get('link')
            
            # Guardar mensaje
            self._save_message(
                whatsapp_message_id=message_id,
                sender_phone=from_phone,
                receiver_phone=self.phone_number_id,
                content=content,
                media_url=media_url,
                message_type=message_type,
                direction='inbound',
                is_automated=False
            )
            
            # Aquí se procesaría con IA (ver ai_service.py)
            # Por ahora solo lo guardamos
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error procesando mensaje entrante: {str(e)}")
            return False
    
    def _save_message(self, whatsapp_message_id, sender_phone, receiver_phone,
                     content, direction, is_automated, message_type='text',
                     media_url=None, order_id=None):
        """Guarda un mensaje en la base de datos."""
        try:
            message = Message(
                whatsapp_message_id=whatsapp_message_id,
                sender_phone=sender_phone,
                receiver_phone=receiver_phone,
                content=content,
                media_url=media_url,
                message_type=message_type,
                direction=direction,
                is_automated=is_automated,
                order_id=order_id,
                status='sent'
            )
            
            db.session.add(message)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error guardando mensaje: {str(e)}")
    
    def verify_webhook(self, mode, token, challenge):
        """
        Verifica el webhook de WhatsApp.
        
        Args:
            mode: Modo de verificación
            token: Token de verificación
            challenge: Challenge enviado por WhatsApp
            
        Returns:
            str or None: Challenge si es válido
        """
        verify_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN')
        
        if mode == 'subscribe' and token == verify_token:
            return challenge
        return None
