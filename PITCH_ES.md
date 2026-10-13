# SatGate — checkout de Bitcoin/Lightning (prototipo)

**Repositorio:** https://github.com/Trelliz/satgate
**Demo estática (sin fondos):** https://trelliz.github.io/satgate/

## Problema
Aceptar pagos de Bitcoin Lightning puede resultar difícil para pequeños comerciantes: hay que administrar un catálogo, crear facturas, evitar cargos duplicados y verificar los estados de pago.

## Nuestra propuesta
SatGate es un checkout gratuito y de código abierto pensado para integrarse con BTCPay Server. Se enfoca en precios definidos en el servidor, claves de idempotencia, estados persistentes y validación segura del pago.

## Estado REAL del proyecto
- Publicado: prototipo funcional con Python, SQLite y pruebas automáticas, que opera **solo en modo simulación**.
- Demo web: un recorrido visual **100% simulado, sin pagos**.
- Preparado fuera del repositorio: paquete ampliado con un adaptador experimental de BTCPay y 18 pruebas; pendiente de revisión e integración.
- No se ha demostrado ninguna transacción real ni se han conectado billeteras.

## Prueba rápida
`python3 -m unittest discover -s tests -v`
`python3 src/satgate.py`
Abrir http://127.0.0.1:8765, seleccionar un producto y utilizar «Simulate successful payment». ¡No enviar bitcoins!

## Licencia
MIT.

## Para un jurado
Evaluar experiencia del usuario, la arquitectura de base, las pruebas y el roadmap. El modo simulado no equivale a una solución de producción. La seguridad y las integraciones reales requieren más trabajo.
