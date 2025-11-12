"""
Script para inicializar la base de datos con datos de prueba.
Ejecutar con: python -m app.scripts.seed_database
"""
import os
import sys
from datetime import datetime, timezone, timedelta
import random

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.extensions import db
from app.data.models import (
    User, Business, Customer, Product, Order, OrderItem,
    Message, Notification, Payment, Worker
)


def seed_database():
    """Llena la base de datos con datos de prueba."""
    # Determinar config según variable de entorno
    config = os.getenv('FLASK_CONFIG', 'development')
    app = create_app(config)
    
    with app.app_context():
        print("Iniciando seed de base de datos...")
        
        # Limpiar datos existentes
        print("🧹 Limpiando datos existentes...")
        db.drop_all()
        db.create_all()
        
        # Crear usuario de prueba
        print("Creando usuarios...")
        user1 = User(
            email='admin@prontoa.com',
            full_name='Alexis Mendoza',
            phone='+573001234567',
            is_active=True,
            is_admin=True
        )
        user1.set_password('admin123')
        db.session.add(user1)
        db.session.flush()
        
        # Crear negocio
        print("Creando negocios...")
        business1 = Business(
            user_id=user1.id,
            name='Panadería El Trigo Dorado',
            business_type='bakery',
            address='Calle 72 #52-42, Barrio El Prado',
            city='Barranquilla',
            whatsapp_number='+573001234567',
            opening_time=datetime.strptime('08:00', '%H:%M').time(),
            closing_time=datetime.strptime('20:00', '%H:%M').time(),
            delivery_enabled=True,
            pickup_enabled=True,
            subscription_plan='pro'
        )
        db.session.add(business1)
        db.session.flush()
        
        # Crear trabajadores (2 tipos: planta y repartidor)
        print("Creando trabajadores...")
        workers_data = [
            # Trabajadores en planta (cocina/preparación)
            {
                'email': 'maria.planta@prontoa.com',
                'password': 'worker123',
                'full_name': 'María Pérez',
                'phone': '+573201234567',
                'worker_type': 'planta'
            },
            {
                'email': 'carlos.planta@prontoa.com',
                'password': 'worker123',
                'full_name': 'Carlos López',
                'phone': '+573202345678',
                'worker_type': 'planta'
            },
            # Trabajadores repartidores (delivery)
            {
                'email': 'juan.repartidor@prontoa.com',
                'password': 'worker123',
                'full_name': 'Juan García',
                'phone': '+573203456789',
                'worker_type': 'repartidor'
            },
            {
                'email': 'ana.repartidor@prontoa.com',
                'password': 'worker123',
                'full_name': 'Ana Rodríguez',
                'phone': '+573204567890',
                'worker_type': 'repartidor'
            }
        ]
        
        workers = []
        for worker_data in workers_data:
            worker = Worker(
                business_id=business1.id,
                email=worker_data['email'],
                full_name=worker_data['full_name'],
                phone=worker_data['phone'],
                worker_type=worker_data['worker_type'],
                is_active=True
            )
            worker.set_password(worker_data['password'])
            workers.append(worker)
            db.session.add(worker)
        
        db.session.flush()
        print(f"   ✓ {len(workers)} trabajadores creados")
        
        # Crear productos
        print("Creando productos...")
        products_data = [
            {'name': 'Pan Francés', 'price': 1500, 'category': 'Panadería', 'stock': 100},
            {'name': 'Croissant', 'price': 3500, 'category': 'Panadería', 'stock': 50},
            {'name': 'Pan Integral', 'price': 4000, 'category': 'Panadería', 'stock': 40},
            {'name': 'Empanada', 'price': 2000, 'category': 'Comida', 'stock': 80},
            {'name': 'Arepa con Queso', 'price': 3000, 'category': 'Comida', 'stock': 60},
            {'name': 'Torta de Chocolate', 'price': 35000, 'category': 'Postres', 'stock': 10},
            {'name': 'Jugo Natural', 'price': 4000, 'category': 'Bebidas', 'stock': 30},
            {'name': 'Café', 'price': 2500, 'category': 'Bebidas', 'stock': 100}
        ]
        
        products = []
        for prod_data in products_data:
            product = Product(
                business_id=business1.id,
                name=prod_data['name'],
                description=f'{prod_data["name"]} fresco y delicioso',
                price=prod_data['price'],
                category=prod_data['category'],
                is_available=True,
                stock_quantity=prod_data['stock']
            )
            products.append(product)
            db.session.add(product)
        
        db.session.flush()
        
        # Crear clientes
        print("Creando clientes...")
        customers_data = [
            {'phone': '+573101234567', 'name': 'María García', 'address': 'Calle 80 #45-23'},
            {'phone': '+573102345678', 'name': 'Carlos Rodríguez', 'address': 'Carrera 50 #70-15'},
            {'phone': '+573103456789', 'name': 'Ana Martínez', 'address': 'Calle 85 #52-30'},
            {'phone': '+573104567890', 'name': 'Luis Hernández', 'address': 'Carrera 55 #75-10'},
            {'phone': '+573105678901', 'name': 'Sofia López', 'address': 'Calle 90 #48-20'}
        ]
        
        customers = []
        for cust_data in customers_data:
            customer = Customer(
                phone=cust_data['phone'],
                name=cust_data['name'],
                address=cust_data['address'],
                city='Barranquilla'
            )
            customers.append(customer)
            db.session.add(customer)
        
        db.session.flush()
        
        # Crear pedidos
        print("Creando pedidos...")
        statuses = ['received', 'preparing', 'ready', 'sent', 'paid', 'closed']
        
        # Primero, crear 5 pedidos para HOY (para que aparezcan en las métricas)
        for i in range(5):
            customer = random.choice(customers)
            customer.total_orders += 1
            
            # Pedidos de hoy (últimas 8 horas)
            hours_ago = random.randint(1, 8)
            created_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
            
            order_number = f"{business1.id}{created_at.strftime('%Y%m%d')}{i+1:04d}"
            
            # Estados activos para pedidos de hoy
            status = random.choice(['received', 'preparing', 'ready', 'sent'])
            
            order = Order(
                order_number=order_number,
                business_id=business1.id,
                customer_id=customer.id,
                status=status,
                order_type=random.choice(['delivery', 'pickup']),
                delivery_address=customer.address if random.random() > 0.3 else None,
                created_at=created_at,
                total_amount=0
            )
            
            # Tiempos según estado
            if status in ['preparing', 'ready', 'sent']:
                order.accepted_at = created_at + timedelta(minutes=random.randint(1, 5))
                order.response_time_seconds = random.randint(30, 300)
            
            if status in ['ready', 'sent']:
                order.ready_at = order.accepted_at + timedelta(minutes=random.randint(15, 45))
                order.preparation_time_seconds = random.randint(900, 2700)
            
            if status == 'sent':
                order.sent_at = order.ready_at + timedelta(minutes=random.randint(5, 15))
            
            db.session.add(order)
            db.session.flush()
            
            # Agregar items al pedido
            num_items = random.randint(1, 4)
            total_amount = 0
            
            selected_products = random.sample(products, num_items)
            for product in selected_products:
                quantity = random.randint(1, 3)
                subtotal = product.price * quantity
                total_amount += subtotal
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal
                )
                db.session.add(order_item)
            
            order.total_amount = total_amount
        
        # Luego, crear 45 pedidos históricos (últimos 30 días)
        for i in range(5, 50):
            # Seleccionar cliente aleatorio
            customer = random.choice(customers)
            customer.total_orders += 1
            
            # Fecha de creación (últimos 30 días, excluyendo hoy)
            days_ago = random.randint(1, 30)
            created_at = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Generar número de pedido
            order_number = f"{business1.id}{created_at.strftime('%Y%m%d')}{i+1:04d}"
            
            # Seleccionar estado basado en antigüedad
            if days_ago > 7:
                status = random.choice(['paid', 'closed'])
            elif days_ago > 3:
                status = random.choice(['ready', 'sent', 'paid'])
            else:
                status = random.choice(statuses)
            
            # Crear pedido
            order = Order(
                order_number=order_number,
                business_id=business1.id,
                customer_id=customer.id,
                status=status,
                order_type=random.choice(['delivery', 'pickup']),
                delivery_address=customer.address if random.random() > 0.3 else None,
                created_at=created_at,
                total_amount=0
            )
            
            # Tiempos según estado
            if status in ['preparing', 'ready', 'sent', 'paid', 'closed']:
                order.accepted_at = created_at + timedelta(minutes=random.randint(1, 5))
                order.response_time_seconds = random.randint(30, 300)
            
            if status in ['ready', 'sent', 'paid', 'closed']:
                order.ready_at = order.accepted_at + timedelta(minutes=random.randint(15, 45))
                order.preparation_time_seconds = random.randint(900, 2700)
            
            if status in ['sent', 'paid', 'closed']:
                order.delivered_at = order.ready_at + timedelta(minutes=random.randint(10, 30))
            
            db.session.add(order)
            db.session.flush()
            
            # Agregar items al pedido
            num_items = random.randint(1, 4)
            total_amount = 0
            
            selected_products = random.sample(products, num_items)
            for product in selected_products:
                quantity = random.randint(1, 3)
                subtotal = product.price * quantity
                total_amount += subtotal
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal
                )
                db.session.add(order_item)
            
            order.total_amount = total_amount
            
            # Crear pago si está pagado
            if status in ['paid', 'closed']:
                payment = Payment(
                    order_id=order.id,
                    amount=total_amount,
                    payment_method=random.choice(['cash', 'card', 'transfer']),
                    payment_status='completed',
                    payment_date=order.delivered_at
                )
                db.session.add(payment)
            
            # TODO: Asignar pedidos a trabajadores cuando se implemente la relación many-to-many
            # if status in ['preparing', 'ready'] and workers:
            #     assigned_worker = random.choice(workers)
            #     order.assigned_workers.append(assigned_worker)
        
        # Commit de todos los cambios
        print("💾 Guardando cambios...")
        db.session.commit()
        
        print("✅ Base de datos inicializada exitosamente!")
        print(f"\n📊 Datos creados:")
        print(f"   Usuarios: {User.query.count()}")
        print(f"   Negocios: {Business.query.count()}")
        print(f"   Trabajadores: {Worker.query.count()}")
        print(f"   Clientes: {Customer.query.count()}")
        print(f"   Productos: {Product.query.count()}")
        print(f"   Pedidos: {Order.query.count()}")
        print(f"   Pagos: {Payment.query.count()}")
        print(f"\nCredenciales de prueba:")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"    ADMIN:")
        print(f"      Email: admin@prontoa.com")
        print(f"      Password: admin123")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"    TRABAJADORES EN PLANTA (Cocina):")
        print(f"      1. María Pérez:")
        print(f"         Email: maria.planta@prontoa.com")
        print(f"         Password: worker123")
        print(f"      2. Carlos López:")
        print(f"         Email: carlos.planta@prontoa.com")
        print(f"         Password: worker123")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"    TRABAJADORES REPARTIDORES (Delivery):")
        print(f"      3. Juan García:")
        print(f"         Email: juan.repartidor@prontoa.com")
        print(f"         Password: worker123")
        print(f"      4. Ana Rodríguez:")
        print(f"         Email: ana.repartidor@prontoa.com")
        print(f"         Password: worker123")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == '__main__':
    seed_database()
