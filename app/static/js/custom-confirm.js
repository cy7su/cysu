/**
 * Кастомная замена для confirm() с красивым модальным окном
 */

function customConfirm(message, onConfirm, onCancel = null) {
    const modalId = 'customConfirmModal-' + Date.now();
    
    const modalHtml = `
        <div class="modal fade" id="${modalId}" tabindex="-1" data-bs-backdrop="static">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="background: var(--dp-02); border: 1px solid var(--border-secondary);">
                    <div class="modal-header" style="border-bottom: 1px solid var(--border-secondary);">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle text-warning me-2"></i>
                            Подтверждение
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer" style="border-top: 1px solid var(--border-secondary);">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="${modalId}-cancel">
                            <i class="fas fa-times me-1"></i>Отмена
                        </button>
                        <button type="button" class="btn btn-primary" id="${modalId}-confirm">
                            <i class="fas fa-check me-1"></i>Подтвердить
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Удаляем старое модальное окно если есть
    const oldModal = document.getElementById(modalId);
    if (oldModal) {
        oldModal.remove();
    }
    
    // Добавляем новое
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);
    
    // Обработчик подтверждения
    document.getElementById(`${modalId}-confirm`).addEventListener('click', function() {
        modal.hide();
        if (onConfirm && typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    // Обработчик отмены
    document.getElementById(`${modalId}-cancel`).addEventListener('click', function() {
        modal.hide();
        if (onCancel && typeof onCancel === 'function') {
            onCancel();
        }
    });
    
    // Удаляем модальное окно после закрытия
    modalElement.addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
    
    modal.show();
}

// Экспортируем для использования
window.customConfirm = customConfirm;

// Переопределяем стандартный confirm для совместимости
window.confirmDelete = function(message, formId) {
    customConfirm(message, function() {
        if (formId) {
            document.getElementById(formId).submit();
        }
        return true;
    });
    return false; // Предотвращаем стандартную отправку
};

