// Глобальные переменные
let currentSection = 'dashboard';
let accounts = [];
let incomeCategories = [];
let expenseCategories = [];
let businessDirections = [];
let transactions = [];
let plannedTransactions = [];

// API базовый URL
const API_BASE = '/api';

// Утилитарные функции
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showError(message) {
    alert('Ошибка: ' + message);
}

function showSuccess(message) {
    alert('Успех: ' + message);
}

// API функции
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Загрузка данных
async function loadAccounts() {
    try {
        accounts = await apiCall('/accounts');
        updateAccountSelects();
        updateAccountsList();
    } catch (error) {
        showError('Не удалось загрузить счета');
    }
}

async function loadIncomeCategories() {
    try {
        incomeCategories = await apiCall('/income-categories');
        updateIncomeCategorySelect();
        updateIncomeCategoriesList();
    } catch (error) {
        showError('Не удалось загрузить категории доходов');
    }
}

async function loadExpenseCategories() {
    try {
        expenseCategories = await apiCall('/expense-categories');
        updateExpenseCategorySelect();
        updateExpenseCategoriesList();
    } catch (error) {
        showError('Не удалось загрузить категории расходов');
    }
}

async function loadBusinessDirections() {
    try {
        businessDirections = await apiCall('/business-directions');
        updateBusinessDirectionSelect();
        updateBusinessDirectionsList();
    } catch (error) {
        showError('Не удалось загрузить направления деятельности');
    }
}

async function loadTransactions() {
    try {
        transactions = await apiCall('/transactions');
        updateTransactionsList();
        updateRecentTransactions();
        updateDashboardStats();
    } catch (error) {
        showError('Не удалось загрузить операции');
    }
}

async function loadPlannedTransactions() {
    try {
        plannedTransactions = await apiCall('/planned-transactions');
        updatePlannedTransactionsList();
    } catch (error) {
        showError('Не удалось загрузить плановые операции');
    }
}

// Обновление интерфейса
function updateAccountSelects() {
    const fromAccountSelect = document.getElementById('from-account');
    const toAccountSelect = document.getElementById('to-account');
    
    [fromAccountSelect, toAccountSelect].forEach(select => {
        select.innerHTML = '<option value="">Выберите счет</option>';
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = `${account.name} (${formatCurrency(account.current_balance)})`;
            select.appendChild(option);
        });
    });
}

function updateIncomeCategorySelect() {
    const select = document.getElementById('income-category');
    select.innerHTML = '<option value="">Выберите категорию</option>';
    incomeCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

function updateExpenseCategorySelect() {
    const select = document.getElementById('expense-category');
    select.innerHTML = '<option value="">Выберите категорию</option>';
    expenseCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

function updateBusinessDirectionSelect() {
    const select = document.getElementById('business-direction');
    select.innerHTML = '<option value="">Выберите направление</option>';
    businessDirections.forEach(direction => {
        const option = document.createElement('option');
        option.value = direction.id;
        option.textContent = direction.name;
        select.appendChild(option);
    });
}

function updateAccountsList() {
    const list = document.getElementById('accounts-list');
    list.innerHTML = '';
    
    accounts.forEach(account => {
        const li = document.createElement('li');
        li.className = 'flex justify-between items-center p-2 bg-gray-50 rounded';
        li.innerHTML = `
            <div>
                <span class="font-medium">${account.name}</span>
                <span class="text-sm text-gray-500">(${account.account_type})</span>
            </div>
            <span class="font-bold">${formatCurrency(account.current_balance)}</span>
        `;
        list.appendChild(li);
    });
}

function updateIncomeCategoriesList() {
    const list = document.getElementById('income-categories-list');
    list.innerHTML = '';
    
    incomeCategories.forEach(category => {
        const li = document.createElement('li');
        li.className = 'p-2 bg-gray-50 rounded';
        li.textContent = category.name;
        list.appendChild(li);
    });
}

function updateExpenseCategoriesList() {
    const list = document.getElementById('expense-categories-list');
    list.innerHTML = '';
    
    expenseCategories.forEach(category => {
        const li = document.createElement('li');
        li.className = 'p-2 bg-gray-50 rounded';
        li.textContent = category.name;
        list.appendChild(li);
    });
}

function updateBusinessDirectionsList() {
    const list = document.getElementById('directions-list');
    list.innerHTML = '';
    
    businessDirections.forEach(direction => {
        const li = document.createElement('li');
        li.className = 'p-2 bg-gray-50 rounded';
        li.textContent = direction.name;
        list.appendChild(li);
    });
}

function updateTransactionsList() {
    const list = document.getElementById('transactions-list');
    list.innerHTML = '';
    
    transactions.forEach(transaction => {
        const li = document.createElement('li');
        li.className = `px-4 py-4 ${getTransactionRowClass(transaction.transaction_type)}`;
        
        const typeText = getTransactionTypeText(transaction.transaction_type);
        const categoryText = getCategoryText(transaction);
        const accountText = getAccountText(transaction);
        
        li.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <div class="flex items-center justify-between">
                        <p class="text-sm font-medium text-gray-900">${typeText}</p>
                        <p class="text-sm font-bold text-gray-900">${formatCurrency(transaction.amount)}</p>
                    </div>
                    <p class="text-sm text-gray-500">${categoryText}</p>
                    <p class="text-xs text-gray-400">${accountText}</p>
                    ${transaction.description ? `<p class="text-xs text-gray-600 mt-1">${transaction.description}</p>` : ''}
                </div>
                <div class="ml-4 text-right">
                    <p class="text-xs text-gray-500">${formatDate(transaction.transaction_date)}</p>
                </div>
            </div>
        `;
        list.appendChild(li);
    });
}

function updateRecentTransactions() {
    const list = document.getElementById('recent-transactions');
    list.innerHTML = '';
    
    const recentTransactions = transactions.slice(0, 5);
    
    recentTransactions.forEach(transaction => {
        const li = document.createElement('li');
        li.className = `px-4 py-4 ${getTransactionRowClass(transaction.transaction_type)}`;
        
        const typeText = getTransactionTypeText(transaction.transaction_type);
        const categoryText = getCategoryText(transaction);
        
        li.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-900">${typeText}</p>
                    <p class="text-sm text-gray-500">${categoryText}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-bold text-gray-900">${formatCurrency(transaction.amount)}</p>
                    <p class="text-xs text-gray-500">${formatDate(transaction.transaction_date)}</p>
                </div>
            </div>
        `;
        list.appendChild(li);
    });
}

function updatePlannedTransactionsList() {
    const list = document.getElementById('planned-list');
    list.innerHTML = '';
    
    plannedTransactions.forEach(planned => {
        const li = document.createElement('li');
        const isOverdue = new Date(planned.planned_date) < new Date();
        li.className = `px-4 py-4 ${isOverdue ? 'bg-red-50 border-l-4 border-red-400' : 'bg-gray-50'}`;
        
        const typeText = getTransactionTypeText(planned.transaction_type);
        
        li.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <div class="flex items-center justify-between">
                        <p class="text-sm font-medium text-gray-900">${typeText}</p>
                        <p class="text-sm font-bold text-gray-900">${formatCurrency(planned.amount)}</p>
                    </div>
                    <p class="text-sm text-gray-500">Запланировано на: ${formatDate(planned.planned_date)}</p>
                    ${planned.description ? `<p class="text-xs text-gray-600 mt-1">${planned.description}</p>` : ''}
                    ${isOverdue ? '<p class="text-xs text-red-600 font-medium">Просрочено</p>' : ''}
                </div>
                <div class="ml-4">
                    <button onclick="completePlannedTransaction(${planned.id})" 
                            class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs">
                        Выполнить
                    </button>
                </div>
            </div>
        `;
        list.appendChild(li);
    });
}

function updateDashboardStats() {
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    
    const monthlyTransactions = transactions.filter(t => 
        new Date(t.transaction_date) >= startOfMonth
    );
    
    const monthlyIncome = monthlyTransactions
        .filter(t => t.transaction_type === 'income')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
    const monthlyExpense = monthlyTransactions
        .filter(t => t.transaction_type === 'expense')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
    const totalBalance = accounts.reduce((sum, acc) => sum + parseFloat(acc.current_balance), 0);
    
    document.getElementById('monthly-income').textContent = formatCurrency(monthlyIncome);
    document.getElementById('monthly-expense').textContent = formatCurrency(monthlyExpense);
    document.getElementById('total-balance').textContent = formatCurrency(totalBalance);
}

// Вспомогательные функции для отображения
function getTransactionRowClass(type) {
    switch (type) {
        case 'income': return 'income-row';
        case 'expense': return 'expense-row';
        case 'transfer': return 'transfer-row';
        default: return '';
    }
}

function getTransactionTypeText(type) {
    switch (type) {
        case 'income': return 'Доход';
        case 'expense': return 'Расход';
        case 'transfer': return 'Перевод';
        default: return type;
    }
}

function getCategoryText(transaction) {
    if (transaction.income_category) {
        return transaction.income_category.name;
    }
    if (transaction.expense_category) {
        return transaction.expense_category.name;
    }
    return 'Без категории';
}

function getAccountText(transaction) {
    const parts = [];
    if (transaction.from_account) {
        parts.push(`Из: ${transaction.from_account.name}`);
    }
    if (transaction.to_account) {
        parts.push(`В: ${transaction.to_account.name}`);
    }
    return parts.join(' | ');
}

// Навигация
function showSection(sectionId) {
    // Скрыть все секции
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // Показать выбранную секцию
    document.getElementById(sectionId + '-section').classList.remove('hidden');
    
    // Обновить активную кнопку навигации
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('bg-accent-dark');
    });
    document.getElementById('nav-' + sectionId).classList.add('bg-accent-dark');
    
    currentSection = sectionId;
}

// Модальные окна
function showTransactionModal() {
    document.getElementById('transaction-modal').classList.remove('hidden');
    
    // Установить текущую дату и время
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('transaction-date').value = now.toISOString().slice(0, 16);
    
    updateTransactionFormFields();
}

function hideTransactionModal() {
    document.getElementById('transaction-modal').classList.add('hidden');
    document.getElementById('transaction-form').reset();
}

function updateTransactionFormFields() {
    const type = document.getElementById('transaction-type').value;
    
    // Показать/скрыть поля в зависимости от типа операции
    document.getElementById('from-account-group').style.display = 
        (type === 'expense' || type === 'transfer') ? 'block' : 'none';
    
    document.getElementById('to-account-group').style.display = 
        (type === 'income' || type === 'transfer') ? 'block' : 'none';
    
    document.getElementById('income-category-group').style.display = 
        type === 'income' ? 'block' : 'none';
    
    document.getElementById('expense-category-group').style.display = 
        type === 'expense' ? 'block' : 'none';
}

// Создание операции
async function createTransaction(formData) {
    try {
        const transaction = await apiCall('/transactions', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        showSuccess('Операция успешно создана');
        hideTransactionModal();
        await loadTransactions();
        await loadAccounts(); // Обновить балансы счетов
    } catch (error) {
        showError('Не удалось создать операцию');
    }
}

// Выполнение плановой операции
async function completePlannedTransaction(plannedId) {
    try {
        await apiCall(`/planned-transactions/${plannedId}/complete`, {
            method: 'POST'
        });
        
        showSuccess('Плановая операция выполнена');
        await loadPlannedTransactions();
        await loadTransactions();
        await loadAccounts();
    } catch (error) {
        showError('Не удалось выполнить плановую операцию');
    }
}

// Генерация отчетов
async function generateReports() {
    const startDate = document.getElementById('report-start-date').value;
    const endDate = document.getElementById('report-end-date').value;
    
    if (!startDate || !endDate) {
        showError('Выберите период для отчета');
        return;
    }
    
    try {
        // Отчет по движению денежных средств
        const cashFlowData = await apiCall(`/reports/cash-flow?start_date=${startDate}&end_date=${endDate}`);
        
        document.getElementById('cash-flow-report').innerHTML = `
            <div class="grid grid-cols-3 gap-4">
                <div class="text-center">
                    <p class="text-sm text-gray-500">Доходы</p>
                    <p class="text-lg font-bold text-green-600">${formatCurrency(cashFlowData.total_income)}</p>
                </div>
                <div class="text-center">
                    <p class="text-sm text-gray-500">Расходы</p>
                    <p class="text-lg font-bold text-red-600">${formatCurrency(cashFlowData.total_expense)}</p>
                </div>
                <div class="text-center">
                    <p class="text-sm text-gray-500">Чистый поток</p>
                    <p class="text-lg font-bold ${cashFlowData.net_flow >= 0 ? 'text-green-600' : 'text-red-600'}">
                        ${formatCurrency(cashFlowData.net_flow)}
                    </p>
                </div>
            </div>
        `;
        
        // Отчет по прибылям и убыткам
        const profitLossData = await apiCall(`/reports/profit-loss?start_date=${startDate}&end_date=${endDate}`);
        
        let profitLossHtml = '<div class="space-y-4">';
        
        if (profitLossData.income_by_category.length > 0) {
            profitLossHtml += '<div><h4 class="font-medium text-green-600 mb-2">Доходы по категориям:</h4><ul class="space-y-1">';
            profitLossData.income_by_category.forEach(item => {
                profitLossHtml += `<li class="flex justify-between"><span>${item.category}</span><span>${formatCurrency(item.amount)}</span></li>`;
            });
            profitLossHtml += '</ul></div>';
        }
        
        if (profitLossData.expense_by_category.length > 0) {
            profitLossHtml += '<div><h4 class="font-medium text-red-600 mb-2">Расходы по категориям:</h4><ul class="space-y-1">';
            profitLossData.expense_by_category.forEach(item => {
                profitLossHtml += `<li class="flex justify-between"><span>${item.category}</span><span>${formatCurrency(item.amount)}</span></li>`;
            });
            profitLossHtml += '</ul></div>';
        }
        
        profitLossHtml += '</div>';
        
        document.getElementById('profit-loss-report').innerHTML = profitLossHtml;
        
    } catch (error) {
        showError('Не удалось сгенерировать отчеты');
    }
}

// Инициализация тестовых данных
async function initTestData() {
    try {
        await apiCall('/init-test-data', { method: 'POST' });
        showSuccess('Тестовые данные созданы');
        await loadAllData();
    } catch (error) {
        showError('Не удалось создать тестовые данные');
    }
}

// Загрузка всех данных
async function loadAllData() {
    await Promise.all([
        loadAccounts(),
        loadIncomeCategories(),
        loadExpenseCategories(),
        loadBusinessDirections(),
        loadTransactions(),
        loadPlannedTransactions()
    ]);
}

// Обработчики событий
document.addEventListener('DOMContentLoaded', function() {
    // Навигация
    document.getElementById('nav-dashboard').addEventListener('click', () => showSection('dashboard'));
    document.getElementById('nav-transactions').addEventListener('click', () => showSection('transactions'));
    document.getElementById('nav-planned').addEventListener('click', () => showSection('planned'));
    document.getElementById('nav-reports').addEventListener('click', () => showSection('reports'));
    document.getElementById('nav-settings').addEventListener('click', () => showSection('settings'));
    
    // Модальные окна
    document.getElementById('add-transaction-btn').addEventListener('click', showTransactionModal);
    document.getElementById('cancel-transaction').addEventListener('click', hideTransactionModal);
    
    // Форма операции
    document.getElementById('transaction-type').addEventListener('change', updateTransactionFormFields);
    document.getElementById('transaction-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            transaction_type: document.getElementById('transaction-type').value,
            amount: parseFloat(document.getElementById('transaction-amount').value),
            transaction_date: document.getElementById('transaction-date').value,
            description: document.getElementById('transaction-description').value,
            from_account_id: document.getElementById('from-account').value || null,
            to_account_id: document.getElementById('to-account').value || null,
            income_category_id: document.getElementById('income-category').value || null,
            expense_category_id: document.getElementById('expense-category').value || null,
            business_direction_id: document.getElementById('business-direction').value || null
        };
        
        createTransaction(formData);
    });
    
    // Отчеты
    document.getElementById('generate-reports').addEventListener('click', generateReports);
    
    // Закрытие модального окна по клику вне его
    document.getElementById('transaction-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            hideTransactionModal();
        }
    });
    
    // Инициализация
    initTestData().then(() => {
        showSection('dashboard');
    });
});

