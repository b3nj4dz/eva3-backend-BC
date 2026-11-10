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
});