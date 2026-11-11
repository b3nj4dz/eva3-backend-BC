/**
 * TechRental & Build - Sistema de Interacción Frontend
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Cierre automático de alertas de Bootstrap tras 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Formateo dinámico de inputs numéricos en formularios (si aplica)
    const inputsMoneda = document.querySelectorAll('.input-currency');
    inputsMoneda.forEach((input) => {
        input.addEventListener('input', (e) => {
            let valor = e.target.value.replace(/\D/g, '');
            if (valor) {
                e.target.value = new Intl.NumberFormat('es-CL').format(valor);
            }
        });
    });

    // Enviar automáticamente formularios de filtros cuando cambia su selector.
    document.querySelectorAll('[data-auto-submit]').forEach((control) => {
        control.addEventListener('change', () => {
            control.form?.requestSubmit();
        });
    });

    // Confirmar acciones destructivas configuradas desde la plantilla.
    document.addEventListener('click', (event) => {
        const target = event.target instanceof Element
            ? event.target.closest('[data-confirm]')
            : null;

        if (target && !window.confirm(target.dataset.confirm)) {
            event.preventDefault();
        }
    });
});