"""
Servicio de Inteligencia Artificial para procesamiento de pedidos..
"""
import openai
import json
import re
from flask import current_app
from app.extensions import db
from app.data.models import AIConversation, Product, Order
from app.services.order_service import OrderService


class AIAgentService:
    """Servicio de agente IA para procesamiento de pedidos."""
    
    def __init__(self):
        # Configurar para Perplexity AI
        openai.api_key = current_app.config.get('PERPLEXITY_API_KEY')
        openai.api_base = "https://api.perplexity.ai"
        self.model = current_app.config.get('PERPLEXITY_MODEL', 'llama-3.1-sonar-small-128k-online')
    
    def process_message(self, customer_phone, message_text, business_id, channel='whatsapp'):
        """
        Procesa un mensaje del cliente usando IA.
        
        Args:
            customer_phone: Teléfono del cliente
            message_text: Texto del mensaje
            business_id: ID del negocio
            
        Returns:
            dict: Resultado del procesamiento con intent y entities
        """
        try:
            # Obtener contexto previo si existe
            conversation = AIConversation.query.filter_by(
                customer_phone=customer_phone,
                business_id=business_id
            ).order_by(AIConversation.updated_at.desc()).first()
            
            context = conversation.conversation_context if conversation else []
            
            # Agregar mensaje actual al contexto
            context.append({
                'role': 'user',
                'content': message_text
            })
            
            # Obtener catálogo de productos
            products = Product.query.filter_by(
                business_id=business_id,
                is_available=True
            ).all()
            
            products_info = "\n".join([
                f"- {p.name}: ${p.price:,.0f} ({p.category})"
                for p in products
            ])
            
            # Crear prompt CORTO y RESTRICTIVO para ahorrar tokens
            system_prompt = f"""Asistente de pedidos. Solo procesa pedidos del catálogo.

    CATÁLOGO:
    {products_info}

    REGLAS ESTRICTAS:
    1. SOLO habla de productos del catálogo
    2. Respuestas CORTAS (máx 2 líneas)
    3. NO respondas temas fuera del negocio
    4. Si preguntan otra cosa: "Solo tomo pedidos"

    REQUISITOS PARA PEDIDO COMPLETO:
    - Mínimo un producto válido del catálogo con cantidad
    - Nombre del cliente
    - delivery_type definido (delivery o pickup)
    - Si delivery_type=delivery, dirección obligatoria
    - Si pickup, dirección opcional
    - ready_to_create_order SOLO puede ser true cuando TODOS los campos estén completos
    En caso contrario, indica missing_info y needs_more_info=true.

    Responde JSON:
    {{
        "intent": "hacer_pedido|consulta|saludo|otro",
        "confidence": 0.95,
        "entities": {{
            "products": [{{"name": "producto", "quantity": 1, "unit_price": 5000}}],
            "delivery_type": "delivery|pickup",
            "address": "direccion",
            "customer_name": "nombre"
        }},
        "response": "Respuesta CORTA",
        "needs_more_info": true/false,
        "missing_info": ["direccion"],
        "ready_to_create_order": true/false
    }}""".strip()
            
            # Llamar a Perplexity AI (compatible con OpenAI)
            messages = [
                {'role': 'system', 'content': system_prompt},
                *context[-5:]  # Últimos 5 mensajes de contexto
            ]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Más determinista, menos creativo
                max_tokens=200    # LIMITE CORTO: Solo 200 tokens
            )
            
            # Parsear respuesta
            ai_response = response.choices[0].message.content
            
            # Intentar extraer JSON de la respuesta
            try:
                # Buscar JSON en la respuesta
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(ai_response)
            except json.JSONDecodeError:
                # Si no se puede parsear, crear respuesta básica
                result = {
                    'intent': 'otro',
                    'confidence': 0.5,
                    'entities': {},
                    'response': ai_response,
                    'needs_more_info': False,
                    'ready_to_create_order': False
                }
            
            # Validar campos obligatorios antes de guardar
            self._enforce_required_fields(result)

            # Guardar o actualizar conversación
            if conversation:
                conversation.conversation_context = context + [{
                    'role': 'assistant',
                    'content': result['response']
                }]
                conversation.extracted_intent = result['intent']
                conversation.extracted_entities = result['entities']
                conversation.confidence_score = result['confidence']
            else:
                conversation = AIConversation(
                    customer_phone=customer_phone,
                    business_id=business_id,
                    conversation_context=context + [{
                        'role': 'assistant',
                        'content': result['response']
                    }],
                    extracted_intent=result['intent'],
                    extracted_entities=result['entities'],
                    confidence_score=result['confidence']
                )
                db.session.add(conversation)
            
            db.session.commit()
            
            # Si el pedido está listo, crear automáticamente
            if result.get('ready_to_create_order') and result['intent'] == 'hacer_pedido':
                order_created, order = self._auto_create_order(
                    business_id=business_id,
                    customer_phone=customer_phone,
                    ai_result=result,
                    channel=channel
                )

                if order_created and order:
                    result['order_created'] = True
                    result['order_number'] = order.order_number
                    if result.get('response'):
                        result['response'] = f"{result['response']}\n\nPedido #{order.order_number} registrado ✅"
                    else:
                        result['response'] = f"Pedido #{order.order_number} registrado ✅"
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error en proceso de IA: {str(e)}")
            return {
                'intent': 'error',
                'confidence': 0,
                'entities': {},
                'response': 'Disculpa, tuve un problema procesando tu mensaje. ¿Podrías repetirlo?',
                'needs_more_info': False,
                'ready_to_create_order': False
            }
    
    def _auto_create_order(self, business_id, customer_phone, ai_result, channel='whatsapp'):
        """
        Crea automáticamente un pedido basado en la respuesta de IA.
        
        Args:
            business_id: ID del negocio
            customer_phone: Teléfono del cliente
            ai_result: Resultado del procesamiento de IA
        """
        try:
            entities = ai_result.get('entities', {})
            products_data = entities.get('products', [])
            
            if not products_data:
                return
            
            # Buscar productos en la base de datos y crear items
            items = []
            for prod_data in products_data:
                product = Product.query.filter_by(
                    business_id=business_id,
                    name=prod_data['name']
                ).first()
                
                if product:
                    items.append({
                        'product_id': product.id,
                        'quantity': prod_data.get('quantity', 1)
                    })
            
            if not items:
                return
            
            # Crear pedido
            order_type = entities.get('delivery_type', 'delivery')
            delivery_address = entities.get('address')
            customer_name = entities.get('customer_name')
            
            success, message, order = OrderService.create_order(
                business_id=business_id,
                customer_phone=customer_phone,
                items_data=items,
                order_type=order_type,
                delivery_address=delivery_address,
                customer_name=customer_name,
                notes='Pedido creado automáticamente por IA'
            )
            
            if success:
                current_app.logger.info(f"Pedido {order.order_number} creado automáticamente")
                self._notify_order_created(order, channel)
                return True, order
            
            current_app.logger.warning(f"No se pudo crear pedido automáticamente: {message}")
            return False, None
            
        except Exception as e:
            current_app.logger.error(f"Error creando pedido automático: {str(e)}")
            return False, None

    def _enforce_required_fields(self, result):
        """Revisa campos obligatorios para crear pedidos y ajusta flags."""
        try:
            entities = result.setdefault('entities', {})
            missing = set()

            products = entities.get('products') or []
            valid_products = []
            for prod in products:
                name = (prod or {}).get('name')
                quantity = max(1, (prod or {}).get('quantity', 1))
                if name:
                    valid_products.append({
                        'name': name,
                        'quantity': quantity,
                        'unit_price': (prod or {}).get('unit_price')
                    })
            entities['products'] = valid_products
            if not valid_products:
                missing.add('products')

            customer_name = (entities.get('customer_name') or '').strip()
            entities['customer_name'] = customer_name or None
            if not customer_name:
                missing.add('customer_name')

            delivery_type = (entities.get('delivery_type') or '').lower()
            if delivery_type not in {'delivery', 'pickup'}:
                missing.add('delivery_type')
            else:
                entities['delivery_type'] = delivery_type
                if delivery_type == 'delivery':
                    address = (entities.get('address') or '').strip()
                    entities['address'] = address or None
                    if not address:
                        missing.add('address')

            if missing:
                result['ready_to_create_order'] = False
                result['needs_more_info'] = True
                existing = set(result.get('missing_info', []))
                result['missing_info'] = list(existing.union(missing))
            else:
                result.setdefault('missing_info', [])
                result.setdefault('needs_more_info', False)

        except Exception as exc:
            current_app.logger.error(f"Error validando campos obligatorios: {exc}")

    def _notify_order_created(self, order, channel):
        """Envía la confirmación de pedido al canal correspondiente."""
        try:
            if channel == 'telegram':
                from app.services.telegram_service import TelegramService
                TelegramService().send_order_confirmation(order)
            else:
                from app.services.whatsapp_service import WhatsAppService
                WhatsAppService().send_order_confirmation(order)
        except Exception as exc:
            current_app.logger.error(f"No se pudo notificar pedido en {channel}: {exc}")
    
    def generate_response(self, intent, context=None):
        """
        Genera una respuesta basada en la intención.
        
        Args:
            intent: Intención detectada
            context: Contexto adicional
            
        Returns:
            str: Respuesta generada
        """
        responses = {
            'saludo': '¡Hola! Bienvenido. ¿En qué puedo ayudarte hoy?',
            'consulta': 'Claro, con gusto te ayudo. ¿Qué necesitas saber?',
            'queja': 'Lamento mucho los inconvenientes. Déjame ayudarte a resolver esto.',
            'despedida': '¡Hasta pronto! Gracias por tu preferencia.'
        }
        
        return responses.get(intent, 'Estoy aquí para ayudarte. ¿Qué necesitas?')
    
    def extract_order_from_text(self, text, products_list):
        """
        Extrae información de pedido de un texto.
        
        Args:
            text: Texto del mensaje
            products_list: Lista de productos disponibles
            
        Returns:
            dict: Información extraída
        """
        # Implementación simplificada
        # En producción, esto sería más robusto con NLP
        
        extracted = {
            'products': [],
            'quantities': [],
            'confidence': 0.7
        }
        
        text_lower = text.lower()
        
        # Buscar productos mencionados
        for product in products_list:
            if product.name.lower() in text_lower:
                # Buscar cantidad cerca del nombre del producto
                quantity = self._extract_quantity_near(text_lower, product.name.lower())
                
                extracted['products'].append(product)
                extracted['quantities'].append(quantity)
        
        return extracted
    
    def _extract_quantity_near(self, text, product_name):
        """Extrae cantidad cerca del nombre del producto."""
        # Buscar patrones como "2 pizzas", "3x hamburguesas", etc.
        patterns = [
            r'(\d+)\s*x?\s*' + re.escape(product_name),
            re.escape(product_name) + r'\s*x?\s*(\d+)',
            r'(\d+)\s*' + re.escape(product_name)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return 1  # Default


def init_ai_service(app):
    """Inicializa el servicio de IA con la configuración de la app."""
    if not app.config.get('PERPLEXITY_API_KEY'):
        app.logger.warning('PERPLEXITY_API_KEY no configurada. El servicio de IA no funcionará.')
