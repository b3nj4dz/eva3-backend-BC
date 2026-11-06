# TechRental & Build - Sistema de Cotización y Arriendo de Flotas TI

Plataforma web desarrollada en Django y Bootstrap 5 para la gestión de arriendo de equipamiento informático empresarial y armado de computadores a medida.

## 📋 Ficha de Registro del Proyecto

* **Nombre de la Organización:** TechRental & Build Chile
* **Modelo de Negocio / Giro:** Arriendo de equipamiento informático para empresas y servicios de armado de PCs
* **Integrantes del Equipo:** Benjamin Canales 21.788.262-1
* **Entidad de Contexto / Agrupación (ORM):** `CategoriaEquipo`
* **Entidad Principal Gestionable (ORM):** `EquipoInformatico`
* **Propósito de la Sesión (`request.session`):** Cotizador de flota con cálculo transitorio de días de arriendo, IVA (19%) y garantía reembolsable.

---

## 🤖 Bitácora de Prompts e Inteligencia Artificial

### Casos de Uso Documentados:

1. **Caso 1: Arquitectura ORM y Integridad Referencial**
   * **Prompt:** *"¿Cómo definir la relación entre CategoriaEquipo y EquipoInformatico en Django para evitar el borrado en cascada y aplicar validaciones de valores numéricos no negativos?"*
   * **Respuesta Técnica:** Se recomendó el uso de `on_delete=models.PROTECT` para proteger la integridad referencial y `MinValueValidator(0)` en `tarifa_diaria` y `monto_garantia`.
   * **Adaptación Aplicada:** Se integró en `apps/inventario/models.py`.

2. **Caso 2: Manipulación de Sesión HTTP (`request.session`)**
   * **Prompt:** *"Necesito implementar una canasta en request.session en Django que acumule equipos, permita modificar la cantidad de días de uso por ítem y calcule subtotal, IVA del 19% y garantía."*
   * **Respuesta Técnica:** Uso de diccionarios dentro de `request.session`, bandera `request.session.modified = True` y Context Processor global para el contador del Navbar.
   * **Adaptación Aplicada:** Se programaron las funciones en `apps/cotizaciones/views.py` y `context_processors.py`.

3. **Caso 3: Seguridad de Vistas y Roles (Decoradores)**
   * **Prompt:** *"¿Cómo restringir el acceso a las vistas de creación, edición y eliminación de equipos solo a usuarios administradores o personal de tienda en Django?"*
   * **Respuesta Técnica:** Uso combinado de los decoradores `@login_required` y `@user_passes_test(es_administrador)`.
   * **Adaptación Aplicada:** Aplicado a todas las rutas de Backoffice en `apps/inventario/views.py`.

---