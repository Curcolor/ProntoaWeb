"""
Blueprint de API para webhook de WhatsApp.
Recibe y procesa mensajes entrantes de WhatsApp Business API.
"""
from flask import Blueprint, request, jsonify, current_app
from app.services.whatsapp_service import WhatsAppService
from app.services.ai_service import AIAgentService

whatsapp_api_bp = Blueprint('whatsapp_api', __name__, url_prefix='/api/whatsapp')


@whatsapp_api_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Verifica el webhook de WhatsApp.
    Este endpoint es llamado por Meta/Facebook para verificar el webhook.
    """
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        whatsapp = WhatsAppService()
        result = whatsapp.verify_webhook(mode, token, challenge)
        
        if result:
            return result, 200
        else:
            return 'Forbidden', 403
            
    except Exception as e:
        current_app.logger.error(f"Error en verificación de webhook: {str(e)}")
        return 'Error', 500


@whatsapp_api_bp.route('/webhook', methods=['POST'])
def receive_message():
    """
    Recibe mensajes entrantes de WhatsApp.
    Procesa el mensaje y genera una respuesta automática.
    """
    try:
        data = request.get_json()
        
        # Verificar que sea un mensaje válido
        if not data or 'entry' not in data:
            return jsonify({'success': True}), 200
        
        # Procesar cada entrada
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('field') != 'messages':
                    continue
                
                value = change.get('value', {})
                
                # Obtener información del mensaje
                if 'messages' in value:
                    for message in value['messages']:
                        # Extraer información
                        from_phone = message.get('from')
                        message_type = message.get('type')
                        message_id = message.get('id')
                        
                        # Procesar solo mensajes de texto por ahora
                        if message_type == 'text':
                            text_content = message.get('text', {}).get('body')
                            
                            # Guardar mensaje
                            whatsapp = WhatsAppService()
                            whatsapp.process_incoming_message({
                                'id': message_id,
                                'from': from_phone,
                                'type': message_type,
                                'text': {'body': text_content}
                            })
                            
                            # Procesar con IA
                            # Nota: Necesitamos determinar el business_id del número de WhatsApp
                            business_id = _get_business_id_from_phone(value.get('metadata', {}).get('phone_number_id'))
                            
                            if business_id:
                                ai_agent = AIAgentService()
                                result = ai_agent.process_message(
                                    customer_phone=from_phone,
                                    message_text=text_content,
                                    business_id=business_id,
                                    channel='whatsapp'
                                )
                                
                                # Enviar respuesta automática
                                response_text = result.get('response')
                                if response_text:
                                    whatsapp.send_message(
                                        to_phone=from_phone,
                                        message_text=response_text
                                    )
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error procesando mensaje de WhatsApp: {str(e)}")
        # Siempre retornar 200 para que WhatsApp no reintente
        return jsonify({'success': True}), 200


@whatsapp_api_bp.route('/send', methods=['POST'])
def send_message():
    """
    Envía un mensaje de WhatsApp manualmente.
    Requiere autenticación.
    """
    try:
        from flask_login import login_required, current_user
        
        data = request.get_json()
        
        phone = data.get('phone')
        message = data.get('message')
        order_id = data.get('order_id')
        
        if not phone or not message:
            return jsonify({
                'success': False,
                'message': 'Teléfono y mensaje son requeridos'
            }), 400
        
        whatsapp = WhatsAppService()
        success, message_id = whatsapp.send_message(
            to_phone=phone,
            message_text=message,
            order_id=order_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Mensaje enviado',
                'message_id': message_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Error enviando mensaje'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


def _get_business_id_from_phone(phone_number_id):
    """
    Obtiene el business_id asociado a un phone_number_id de WhatsApp.
    
    Args:
        phone_number_id: ID del número de teléfono de WhatsApp
        
    Returns:
        int: ID del negocio o None
    """
    try:
        from app.data.models import Business
        
        # En producción, esto debería estar mapeado en la configuración
        # Por ahora, buscamos el primer negocio activo
        business = Business.query.filter_by(is_active=True).first()
        
        return business.id if business else None
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo business_id: {str(e)}")
        return None
