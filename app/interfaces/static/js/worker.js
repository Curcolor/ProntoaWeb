// worker.js - Manejo simple de pedidos para trabajador

document.addEventListener('DOMContentLoaded', () => {
  console.log('✓ Worker dashboard listo');
  
  // Agregar event listeners a botones de despacho
  document.querySelectorAll('.btn-dispatch').forEach(btn => {
    btn.addEventListener('click', function() {
      const orderId = this.dataset.orderId;
      dispatchOrder(orderId, this);
    });
  });
});

function dispatchOrder(orderId, button) {
  // Deshabilitar botón
  button.disabled = true;
  button.textContent = 'Despachando...';
  
  // Simular envío a servidor
  setTimeout(() => {
    // Marcar como despachado
    const card = document.querySelector(`[data-order-id="${orderId}"]`);
    card.classList.add('dispatched');
    
    const status = card.querySelector('.order-status');
    status.textContent = 'Despachado';
    status.className = 'order-status despachado';
    
    button.textContent = '✓ Despachado';
    button.disabled = true;
    
    console.log(`Pedido ${orderId} despachado`);
  }, 600);
}
