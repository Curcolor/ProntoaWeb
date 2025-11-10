# Ejemplos de Uso de la API - ProntoaWeb

## Base URL
```
http://127.0.0.1:5000/api
```

---

## Autenticación

### Registro de Usuario
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "full_name": "Juan Pérez",
    "phone": "+573001234567",
    "business_name": "Restaurante El Buen Sabor",
    "business_type": "restaurant"
  }'
```

### Login
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@prontoa.com",
    "password": "admin123",
    "remember": false
  }'
```

### Obtener Usuario Actual
```bash
curl -X GET http://127.0.0.1:5000/api/auth/me \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## Pedidos

### Listar Todos los Pedidos
```bash
curl -X GET http://127.0.0.1:5000/api/orders \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Listar Pedidos por Estado
```bash
curl -X GET "http://127.0.0.1:5000/api/orders?status=received" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Crear Nuevo Pedido
```bash
curl -X POST http://127.0.0.1:5000/api/orders \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "customer_phone": "+573101234567",
    "customer_name": "María García",
    "order_type": "delivery",
    "delivery_address": "Calle 80 #45-23, Barranquilla",
    "notes": "Sin cebolla por favor",
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      },
      {
        "product_id": 3,
        "quantity": 1
      }
    ]
  }'
```

### Obtener Pedido Específico
```bash
curl -X GET http://127.0.0.1:5000/api/orders/1 \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Actualizar Estado del Pedido
```bash
curl -X PATCH http://127.0.0.1:5000/api/orders/1 \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "status": "preparing"
  }'
```

Estados válidos:
- `received` - Recibido
- `preparing` - En preparación
- `ready` - Listo
- `sent` - Enviado
- `paid` - Pagado
- `closed` - Cerrado
- `cancelled` - Cancelado

### Cancelar Pedido
```bash
curl -X POST http://127.0.0.1:5000/api/orders/1/cancel \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "reason": "Cliente canceló el pedido"
  }'
```

### Obtener Conteos por Estado
```bash
curl -X GET http://127.0.0.1:5000/api/orders/by-status \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## KPIs y Métricas

### Métricas del Dashboard
```bash
curl -X GET http://127.0.0.1:5000/api/kpis/dashboard \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

Respuesta esperada:
```json
{
  "success": true,
  "metrics": {
    "orders_today": 24,
    "avg_response_time": 4.2,
    "sales_today": 850000,
    "satisfaction": 98.5
  }
}
```

### Comparaciones de KPIs
```bash
curl -X GET "http://127.0.0.1:5000/api/kpis/comparisons?period_days=30" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Métricas Operativas
```bash
curl -X GET "http://127.0.0.1:5000/api/kpis/operational?period_days=30" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Impacto Financiero
```bash
curl -X GET "http://127.0.0.1:5000/api/kpis/financial?period_days=30" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Distribución de Pedidos por Hora
```bash
curl -X GET "http://127.0.0.1:5000/api/kpis/orders-by-hour?days=7" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Resumen Completo
```bash
curl -X GET "http://127.0.0.1:5000/api/kpis/summary?period_days=30" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## WhatsApp

### Enviar Mensaje Manual
```bash
curl -X POST http://127.0.0.1:5000/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "phone": "+573101234567",
    "message": "Hola! Tu pedido está listo para ser recogido.",
    "order_id": 1
  }'
```

### Webhook (Para Meta/Facebook)
```bash
# Verificación del webhook
curl -X GET "http://127.0.0.1:5000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=prontoa-verify-token&hub.challenge=CHALLENGE_STRING"

# Recibir mensaje (POST desde Meta)
curl -X POST http://127.0.0.1:5000/api/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [
      {
        "changes": [
          {
            "field": "messages",
            "value": {
              "messages": [
                {
                  "id": "wamid.123",
                  "from": "573101234567",
                  "type": "text",
                  "text": {
                    "body": "Hola, quiero ordenar 2 panes y 1 café"
                  }
                }
              ]
            }
          }
        ]
      }
    ]
  }'
```

---

## Ejemplos con JavaScript (Fetch API)

### Login desde Frontend
```javascript
async function login(email, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Importante para cookies
    body: JSON.stringify({
      email: email,
      password: password,
      remember: false
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Login exitoso:', data.user);
    window.location.href = '/dashboard';
  } else {
    console.error('Error:', data.message);
  }
}
```

### Obtener Pedidos
```javascript
async function getOrders(status = null) {
  const url = status 
    ? `/api/orders?status=${status}` 
    : '/api/orders';
    
  const response = await fetch(url, {
    credentials: 'include'
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Pedidos:', data.orders);
    return data.orders;
  }
}
```

### Actualizar Estado de Pedido
```javascript
async function updateOrderStatus(orderId, newStatus) {
  const response = await fetch(`/api/orders/${orderId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      status: newStatus
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Pedido actualizado:', data.order);
    return data.order;
  }
}
```

### Obtener Métricas del Dashboard
```javascript
async function getDashboardMetrics() {
  const response = await fetch('/api/kpis/dashboard', {
    credentials: 'include'
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Métricas:', data.metrics);
    
    // Actualizar UI
    document.getElementById('orders-today').textContent = data.metrics.orders_today;
    document.getElementById('avg-response').textContent = data.metrics.avg_response_time + ' min';
    document.getElementById('sales-today').textContent = '$' + data.metrics.sales_today.toLocaleString();
    document.getElementById('satisfaction').textContent = data.metrics.satisfaction + '%';
  }
}
```

---

##  Ejemplo de Flujo Completo

### Flujo: Cliente hace pedido por WhatsApp
```
1. Cliente envía mensaje a WhatsApp
   ↓
2. Webhook recibe mensaje en /api/whatsapp/webhook
   ↓
3. AIAgentService procesa el mensaje
   ↓
4. IA extrae productos y cantidades
   ↓
5. Si está completo, crea pedido automáticamente
   ↓
6. WhatsAppService envía confirmación al cliente
   ↓
7. Pedido aparece en dashboard con estado "received"
   ↓
8. Usuario mueve pedido a "preparing" via API
   ↓
9. WhatsAppService notifica al cliente
   ↓
10. Usuario mueve a "ready"
    ↓
11. WhatsAppService notifica que está listo
    ↓
12. Usuario marca como "delivered"
    ↓
13. Se registra el pago
```

---

## Notas Importantes

1. **Autenticación:** La mayoría de endpoints requieren sesión activa (cookie)
2. **CORS:** Ya está configurado para permitir requests desde el frontend
3. **Validación:** Todos los endpoints validan datos de entrada
4. **Errores:** Formato estándar:
   ```json
   {
     "success": false,
     "message": "Descripción del error",
     "errors": {} // Detalles opcionales
   }
   ```

5. **Rate Limiting:** Configurado para prevenir abuso de la API

---

##  Prueba Rápida

```bash
# 1. Login
curl -c cookies.txt -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@prontoa.com", "password": "admin123"}'

# 2. Obtener métricas del dashboard
curl -b cookies.txt http://127.0.0.1:5000/api/kpis/dashboard

# 3. Listar pedidos
curl -b cookies.txt http://127.0.0.1:5000/api/orders
```

---

## Herramientas Recomendadas

- **Postman:** Para probar APIs de forma visual
- **Insomnia:** Alternativa ligera a Postman
- **HTTPie:** Cliente HTTP en terminal más amigable
- **Browser DevTools:** Para debugging del frontend
