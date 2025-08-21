// Основной JavaScript файл для BG Опросника

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initThemeToggle();
    initTooltips();
    initModals();
    initForms();
    initCharts();
});

// Переключение темы
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-bs-theme');
            let newTheme;
            
            if (currentTheme === 'light') {
                newTheme = 'dark';
            } else if (currentTheme === 'dark') {
                newTheme = 'auto';
            } else {
                newTheme = 'light';
            }
            
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

function setTheme(theme) {
    const html = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');
    
    if (theme === 'auto') {
        html.removeAttribute('data-bs-theme');
        if (themeIcon) {
            themeIcon.className = 'bi bi-circle-half';
        }
    } else {
        html.setAttribute('data-bs-theme', theme);
        if (themeIcon) {
            if (theme === 'light') {
                themeIcon.className = 'bi bi-moon-fill';
            } else {
                themeIcon.className = 'bi bi-sun-fill';
            }
        }
    }
}

// Инициализация тултипов
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация модальных окон
function initModals() {
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
}

// Инициализация форм
function initForms() {
    // Валидация форм
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Автосохранение форм
    const autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                autoSaveForm(form);
            });
        });
    });
}

// Автосохранение формы
function autoSaveForm(form) {
    const formData = new FormData(form);
    const url = form.getAttribute('data-auto-save-url');
    
    if (!url) return;
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Форма сохранена', 'success');
        } else {
            showToast('Ошибка сохранения', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка автосохранения:', error);
        showToast('Ошибка сохранения', 'error');
    });
}

// Инициализация графиков
function initCharts() {
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.getAttribute('data-chart');
        const chartData = JSON.parse(element.getAttribute('data-chart-data') || '{}');
        
        if (chartType === 'pie') {
            createPieChart(element, chartData);
        } else if (chartType === 'bar') {
            createBarChart(element, chartData);
        } else if (chartType === 'line') {
            createLineChart(element, chartData);
        }
    });
}

// Создание круговой диаграммы
function createPieChart(element, data) {
    const ctx = element.getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels || [],
            datasets: [{
                data: data.values || [],
                backgroundColor: [
                    '#dc3545', '#6c757d', '#198754', '#fd7e14', '#0dcaf0',
                    '#6f42c1', '#e83e8c', '#20c997', '#ffc107', '#6610f2'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Создание столбчатой диаграммы
function createBarChart(element, data) {
    const ctx = element.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: data.label || 'Данные',
                data: data.values || [],
                backgroundColor: '#dc3545',
                borderColor: '#c82333',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Создание линейной диаграммы
function createLineChart(element, data) {
    const ctx = element.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: data.label || 'Данные',
                data: data.values || [],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Показ уведомлений
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        createToastContainer();
    }
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Создание контейнера для уведомлений
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
}

// Получение CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функции для работы с опросами
const SurveyManager = {
    // Копирование ссылки на опрос
    copySurveyLink: function(surveyId) {
        const link = `${window.location.origin}/surveys/public/${surveyId}/`;
        navigator.clipboard.writeText(link).then(function() {
            showToast('Ссылка скопирована в буфер обмена', 'success');
        }, function() {
            showToast('Ошибка копирования ссылки', 'error');
        });
    },
    
    // Предварительный просмотр опроса
    previewSurvey: function(surveyId) {
        const url = `/surveys/${surveyId}/preview/`;
        window.open(url, '_blank');
    },
    
    // Экспорт результатов
    exportResults: function(surveyId, format = 'csv') {
        const url = `/surveys/${surveyId}/results/export/?format=${format}`;
        window.location.href = url;
    },
    
    // Удаление опроса с подтверждением
    deleteSurvey: function(surveyId, surveyTitle) {
        if (confirm(`Вы уверены, что хотите удалить опрос "${surveyTitle}"? Это действие нельзя отменить.`)) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/surveys/${surveyId}/delete/`;
            
            const csrfToken = document.createElement('input');
            csrfToken.type = 'hidden';
            csrfToken.name = 'csrfmiddlewaretoken';
            csrfToken.value = getCookie('csrftoken');
            
            form.appendChild(csrfToken);
            document.body.appendChild(form);
            form.submit();
        }
    }
};

// Функции для работы с вопросами
const QuestionManager = {
    // Добавление нового вопроса
    addQuestion: function(surveyId) {
        const url = `/surveys/${surveyId}/questions/create/`;
        window.location.href = url;
    },
    
    // Редактирование вопроса
    editQuestion: function(surveyId, questionId) {
        const url = `/surveys/${surveyId}/questions/${questionId}/edit/`;
        window.location.href = url;
    },
    
    // Удаление вопроса
    deleteQuestion: function(surveyId, questionId, questionText) {
        if (confirm(`Удалить вопрос "${questionText}"?`)) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/surveys/${surveyId}/questions/${questionId}/delete/`;
            
            const csrfToken = document.createElement('input');
            csrfToken.type = 'hidden';
            csrfToken.name = 'csrfmiddlewaretoken';
            csrfToken.value = getCookie('csrftoken');
            
            form.appendChild(csrfToken);
            document.body.appendChild(form);
            form.submit();
        }
    },
    
    // Изменение порядка вопросов
    reorderQuestions: function(surveyId) {
        const url = `/surveys/${surveyId}/questions/reorder/`;
        window.location.href = url;
    }
};

// Функции для работы с пользователями
const UserManager = {
    // Активация/деактивация пользователя
    toggleUserStatus: function(userId, currentStatus) {
        const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
        const url = `/users/admin/users/${userId}/toggle-status/`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showToast('Ошибка изменения статуса', 'error');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showToast('Ошибка изменения статуса', 'error');
        });
    },
    
    // Импорт пользователей из LDAP
    importFromLDAP: function() {
        const url = '/users/admin/ldap-import/';
        window.location.href = url;
    }
};

// Глобальные функции
window.SurveyManager = SurveyManager;
window.QuestionManager = QuestionManager;
window.UserManager = UserManager;
window.showToast = showToast;