// BG Survey Platform - Основной JavaScript файл

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initThemeToggle();
    initTooltips();
    initConfirmations();
    initFormValidation();
    initAnimations();
    initMobileMenu();
    initDropdowns();
});

// Переключение темы
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const body = document.body;
            const icon = this.querySelector('i');
            
            if (body.classList.contains('dark-theme')) {
                // Переключение на светлую тему
                body.classList.remove('dark-theme');
                icon.innerHTML = '';
                icon.textContent = '🌙';
                icon.style.fontFamily = 'sans-serif';
                icon.style.fontWeight = 'normal';
                document.cookie = 'theme=light; path=/; max-age=31536000';
                localStorage.setItem('theme', 'light');
            } else {
                // Переключение на темную тему
                body.classList.add('dark-theme');
                icon.innerHTML = '';
                icon.textContent = '☀️';
                icon.style.fontFamily = 'sans-serif';
                icon.style.fontWeight = 'normal';
                document.cookie = 'theme=dark; path=/; max-age=31536000';
                localStorage.setItem('theme', 'dark');
            }
        });
        
        // Установка текущей темы при загрузке
        const savedTheme = localStorage.getItem('theme') || getCookie('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            themeToggle.querySelector('i').className = 'fas fa-sun';
        }
    }
}

// Получение значения cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Инициализация тултипов
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация подтверждений
function initConfirmations() {
    // Подтверждение удаления
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-confirm]')) {
            const message = e.target.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    });
}

// Валидация форм
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

// Функция валидации формы
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Это поле обязательно для заполнения');
            isValid = false;
        } else {
            clearFieldError(field);
        }
        
        // Специальная валидация для email
        if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                showFieldError(field, 'Введите корректный email адрес');
                isValid = false;
            }
        }
        
        // Валидация длины пароля
        if (field.type === 'password' && field.value) {
            if (field.value.length < 6) {
                showFieldError(field, 'Пароль должен содержать минимум 6 символов');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

// Показать ошибку поля
function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.textContent = message;
    
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
}

// Очистить ошибку поля
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Инициализация анимаций
function initAnimations() {
    // Анимация появления элементов при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Наблюдение за элементами для анимации
    const animatedElements = document.querySelectorAll('.card, .feature-icon, .stat-icon');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Функции для работы с опросами
window.surveyUtils = {
    // Копирование ссылки на опрос
    copySurveyUrl: function(url) {
        navigator.clipboard.writeText(url).then(function() {
            showNotification('Ссылка скопирована в буфер обмена', 'success');
        }).catch(function() {
            // Fallback для старых браузеров
            const textArea = document.createElement('textarea');
            textArea.value = url;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showNotification('Ссылка скопирована в буфер обмена', 'success');
        });
    },
    
    // Подтверждение отправки опроса
    confirmSurveySubmission: function() {
        return confirm('Вы уверены, что хотите отправить ответы? После отправки их нельзя будет изменить.');
    },
    
    // Валидация ответов на опрос
    validateSurveyAnswers: function(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
};

// Функции для работы с графиками
window.chartUtils = {
    // Создание круговой диаграммы
    createPieChart: function(canvasId, data, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#dc3545', '#fd7e14', '#ffc107', '#198754', '#0d6efd',
                        '#6f42c1', '#e83e8c', '#20c997', '#6c757d', '#343a40'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: title
                    }
                }
            }
        });
    },
    
    // Создание столбчатой диаграммы
    createBarChart: function(canvasId, data, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Количество',
                    data: values,
                    backgroundColor: '#dc3545',
                    borderColor: '#c82333',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: title
                    }
                }
            }
        });
    }
};

// Функции для работы с уведомлениями
window.notificationUtils = {
    // Показать уведомление
    show: function(message, type = 'info', duration = 5000) {
        showNotification(message, type, duration);
    },
    
    // Показать успешное уведомление
    success: function(message, duration) {
        this.show(message, 'success', duration);
    },
    
    // Показать уведомление об ошибке
    error: function(message, duration) {
        this.show(message, 'error', duration);
    },
    
    // Показать предупреждение
    warning: function(message, duration) {
        this.show(message, 'warning', duration);
    }
};

// Функция показа уведомления
function showNotification(message, type = 'info', duration = 5000) {
    // Создание элемента уведомления
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Добавление в DOM
    document.body.appendChild(notification);
    
    // Автоматическое скрытие
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
    
    // Обработка закрытия
    notification.addEventListener('closed.bs.alert', function() {
        if (notification.parentNode) {
            notification.remove();
        }
    });
}

// Функции для работы с данными
window.dataUtils = {
    // Экспорт данных в CSV
    exportToCSV: function(data, filename) {
        if (!data || !data.length) {
            notificationUtils.error('Нет данных для экспорта');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename || 'export.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    },
    
    // Форматирование даты
    formatDate: function(date, format = 'DD.MM.YYYY') {
        if (!date) return '';
        
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        
        return format
            .replace('DD', day)
            .replace('MM', month)
            .replace('YYYY', year);
    }
};

// Функции для работы с модальными окнами
window.modalUtils = {
    // Показать модальное окно
    show: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    },
    
    // Скрыть модальное окно
    hide: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
};

// Утилиты для работы с DOM
window.domUtils = {
    // Создание элемента с атрибутами
    createElement: function(tag, attributes = {}, textContent = '') {
        const element = document.createElement(tag);
        
        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });
        
        if (textContent) {
            element.textContent = textContent;
        }
        
        return element;
    },
    
    // Добавление/удаление классов
    toggleClass: function(element, className) {
        if (element.classList.contains(className)) {
            element.classList.remove(className);
        } else {
            element.classList.add(className);
        }
    },
    
    // Проверка видимости элемента
    isVisible: function(element) {
        return element.offsetWidth > 0 && element.offsetHeight > 0;
    }
};

// Глобальные обработчики событий
document.addEventListener('click', function(e) {
    // Обработка копирования ссылок
    if (e.target.matches('[data-copy]')) {
        const text = e.target.getAttribute('data-copy');
        surveyUtils.copySurveyUrl(text);
    }
    
    // Обработка подтверждений
    if (e.target.matches('[data-confirm]')) {
        const message = e.target.getAttribute('data-confirm');
        if (!confirm(message)) {
            e.preventDefault();
            e.stopPropagation();
        }
    }
});

// Обработка ошибок
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    notificationUtils.error('Произошла ошибка. Проверьте консоль для деталей.');
});

// Инициализация мобильного меню
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Закрытие меню при клике на ссылку
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarCollapse.classList.remove('show');
            });
        });
        
        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// Инициализация выпадающих меню
function initDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.closest('.dropdown');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            // Закрываем все другие выпадающие меню
            document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                }
            });
            
            // Переключаем текущее меню
            if (menu) {
                menu.classList.toggle('show');
            }
        });
    });
    
    // Закрытие выпадающих меню при клике вне их
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// Обработка необработанных промисов
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    notificationUtils.error('Произошла ошибка при выполнении операции.');
});