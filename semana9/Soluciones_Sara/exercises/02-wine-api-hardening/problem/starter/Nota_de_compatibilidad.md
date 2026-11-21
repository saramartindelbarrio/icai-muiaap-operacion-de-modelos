### Nota de compatibilidad — Wine Quality API v1.1

Esta semana hemos mejorado el contrato público de la API sin modificar sus endpoints existentes.
Añadir el campo `served_at` a la respuesta es un cambio compatible, ya que los clientes anteriores pueden seguir utilizando los campos conocidos.
También hemos documentado los errores, sus códigos y los ejemplos en OpenAPI.
Un cambio que rompería la compatibilidad sería eliminar el campo `quality_band` o cambiar su nombre.
Los clientes de S7 que dependen de ese campo dejarían de funcionar correctamente.
Otro cambio incompatible sería modificar la estructura pública del sobre de error.
Por eso, las mejoras compatibles se publican en la versión `1.1.0`.
Los cambios que rompen el contrato deberían publicarse en una nueva versión mayor, por ejemplo `2.0.0`, manteniendo una estrategia de migración para los clientes anteriores.