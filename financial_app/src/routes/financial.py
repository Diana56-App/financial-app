from flask import Blueprint, request, jsonify
from src.models.financial import (
    db, User, Account, IncomeCategory, ExpenseCategory, 
    BusinessDirection, Transaction, PlannedTransaction,
    TransactionType, AccountType, UserRole
)
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

financial_bp = Blueprint('financial', __name__)

# Утилитарные функции
def get_current_user():
    """Заглушка для получения текущего пользователя. В реальном приложении здесь будет аутентификация."""
    user = User.query.first()
    if not user:
        # Создаем тестового пользователя-администратора
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash='hashed_password',
            role=UserRole.ADMIN
        )
        db.session.add(user)
        db.session.commit()
    return user

def update_account_balance(account_id, amount, operation='add'):
    """Обновление баланса счета"""
    account = Account.query.get(account_id)
    if account:
        if operation == 'add':
            account.current_balance += Decimal(str(amount))
        elif operation == 'subtract':
            account.current_balance -= Decimal(str(amount))
        db.session.commit()

# API для счетов
@financial_bp.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.filter_by(is_active=True).all()
    return jsonify([account.to_dict() for account in accounts])

@financial_bp.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()
    
    account = Account(
        name=data['name'],
        account_type=AccountType(data['account_type']),
        initial_balance=Decimal(str(data.get('initial_balance', 0))),
        current_balance=Decimal(str(data.get('initial_balance', 0))),
        currency=data.get('currency', 'RUB')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify(account.to_dict()), 201

@financial_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    data = request.get_json()
    
    account.name = data.get('name', account.name)
    account.account_type = AccountType(data.get('account_type', account.account_type.value))
    
    db.session.commit()
    return jsonify(account.to_dict())

@financial_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    account.is_active = False
    db.session.commit()
    return jsonify({'message': 'Account deactivated successfully'})

# API для категорий доходов
@financial_bp.route('/income-categories', methods=['GET'])
def get_income_categories():
    categories = IncomeCategory.query.filter_by(is_active=True).all()
    return jsonify([category.to_dict() for category in categories])

@financial_bp.route('/income-categories', methods=['POST'])
def create_income_category():
    data = request.get_json()
    
    category = IncomeCategory(
        name=data['name'],
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

# API для категорий расходов
@financial_bp.route('/expense-categories', methods=['GET'])
def get_expense_categories():
    categories = ExpenseCategory.query.filter_by(is_active=True).all()
    return jsonify([category.to_dict() for category in categories])

@financial_bp.route('/expense-categories', methods=['POST'])
def create_expense_category():
    data = request.get_json()
    
    category = ExpenseCategory(
        name=data['name'],
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

# API для направлений деятельности
@financial_bp.route('/business-directions', methods=['GET'])
def get_business_directions():
    directions = BusinessDirection.query.filter_by(is_active=True).all()
    return jsonify([direction.to_dict() for direction in directions])

@financial_bp.route('/business-directions', methods=['POST'])
def create_business_direction():
    data = request.get_json()
    
    direction = BusinessDirection(name=data['name'])
    
    db.session.add(direction)
    db.session.commit()
    
    return jsonify(direction.to_dict()), 201

# API для транзакций
@financial_bp.route('/transactions', methods=['GET'])
def get_transactions():
    user = get_current_user()
    
    # Фильтры
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('transaction_type')
    account_id = request.args.get('account_id')
    
    query = Transaction.query
    
    # Если пользователь не администратор, показываем только его транзакции
    if user.role != UserRole.ADMIN:
        query = query.filter_by(user_id=user.id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    if transaction_type:
        query = query.filter_by(transaction_type=TransactionType(transaction_type))
    if account_id:
        query = query.filter(or_(
            Transaction.from_account_id == account_id,
            Transaction.to_account_id == account_id
        ))
    
    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    return jsonify([transaction.to_dict() for transaction in transactions])

@financial_bp.route('/transactions', methods=['POST'])
def create_transaction():
    user = get_current_user()
    data = request.get_json()
    
    transaction = Transaction(
        transaction_type=TransactionType(data['transaction_type']),
        amount=Decimal(str(data['amount'])),
        description=data.get('description'),
        transaction_date=datetime.fromisoformat(data.get('transaction_date', datetime.utcnow().isoformat())),
        user_id=user.id,
        from_account_id=data.get('from_account_id'),
        to_account_id=data.get('to_account_id'),
        income_category_id=data.get('income_category_id'),
        expense_category_id=data.get('expense_category_id'),
        business_direction_id=data.get('business_direction_id')
    )
    
    db.session.add(transaction)
    
    # Обновление балансов счетов
    if transaction.transaction_type == TransactionType.INCOME and transaction.to_account_id:
        update_account_balance(transaction.to_account_id, transaction.amount, 'add')
    elif transaction.transaction_type == TransactionType.EXPENSE and transaction.from_account_id:
        update_account_balance(transaction.from_account_id, transaction.amount, 'subtract')
    elif transaction.transaction_type == TransactionType.TRANSFER:
        if transaction.from_account_id:
            update_account_balance(transaction.from_account_id, transaction.amount, 'subtract')
        if transaction.to_account_id:
            update_account_balance(transaction.to_account_id, transaction.amount, 'add')
    
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

# API для плановых транзакций
@financial_bp.route('/planned-transactions', methods=['GET'])
def get_planned_transactions():
    user = get_current_user()
    
    query = PlannedTransaction.query
    
    # Если пользователь не администратор, показываем только его плановые транзакции
    if user.role != UserRole.ADMIN:
        query = query.filter_by(user_id=user.id)
    
    planned_transactions = query.filter_by(is_completed=False).order_by(PlannedTransaction.planned_date).all()
    return jsonify([pt.to_dict() for pt in planned_transactions])

@financial_bp.route('/planned-transactions', methods=['POST'])
def create_planned_transaction():
    user = get_current_user()
    data = request.get_json()
    
    planned_transaction = PlannedTransaction(
        transaction_type=TransactionType(data['transaction_type']),
        amount=Decimal(str(data['amount'])),
        description=data.get('description'),
        planned_date=datetime.fromisoformat(data['planned_date']),
        is_recurring=data.get('is_recurring', False),
        recurrence_pattern=data.get('recurrence_pattern'),
        user_id=user.id,
        from_account_id=data.get('from_account_id'),
        to_account_id=data.get('to_account_id'),
        income_category_id=data.get('income_category_id'),
        expense_category_id=data.get('expense_category_id'),
        business_direction_id=data.get('business_direction_id')
    )
    
    db.session.add(planned_transaction)
    db.session.commit()
    
    return jsonify(planned_transaction.to_dict()), 201

@financial_bp.route('/planned-transactions/<int:pt_id>/complete', methods=['POST'])
def complete_planned_transaction(pt_id):
    planned_transaction = PlannedTransaction.query.get_or_404(pt_id)
    
    # Создаем фактическую транзакцию
    transaction = Transaction(
        transaction_type=planned_transaction.transaction_type,
        amount=planned_transaction.amount,
        description=planned_transaction.description,
        transaction_date=datetime.utcnow(),
        user_id=planned_transaction.user_id,
        from_account_id=planned_transaction.from_account_id,
        to_account_id=planned_transaction.to_account_id,
        income_category_id=planned_transaction.income_category_id,
        expense_category_id=planned_transaction.expense_category_id,
        business_direction_id=planned_transaction.business_direction_id
    )
    
    db.session.add(transaction)
    db.session.flush()  # Получаем ID транзакции
    
    # Обновляем плановую транзакцию
    planned_transaction.is_completed = True
    planned_transaction.completed_transaction_id = transaction.id
    
    # Обновление балансов счетов
    if transaction.transaction_type == TransactionType.INCOME and transaction.to_account_id:
        update_account_balance(transaction.to_account_id, transaction.amount, 'add')
    elif transaction.transaction_type == TransactionType.EXPENSE and transaction.from_account_id:
        update_account_balance(transaction.from_account_id, transaction.amount, 'subtract')
    elif transaction.transaction_type == TransactionType.TRANSFER:
        if transaction.from_account_id:
            update_account_balance(transaction.from_account_id, transaction.amount, 'subtract')
        if transaction.to_account_id:
            update_account_balance(transaction.to_account_id, transaction.amount, 'add')
    
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

# API для отчетов
@financial_bp.route('/reports/cash-flow', methods=['GET'])
def cash_flow_report():
    user = get_current_user()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query
    if user.role != UserRole.ADMIN:
        query = query.filter_by(user_id=user.id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    
    transactions = query.all()
    
    total_income = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.INCOME)
    total_expense = sum(float(t.amount) for t in transactions if t.transaction_type == TransactionType.EXPENSE)
    net_flow = total_income - total_expense
    
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'net_flow': net_flow,
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    })

@financial_bp.route('/reports/profit-loss', methods=['GET'])
def profit_loss_report():
    user = get_current_user()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query
    if user.role != UserRole.ADMIN:
        query = query.filter_by(user_id=user.id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    
    # Группировка по категориям
    income_by_category = db.session.query(
        IncomeCategory.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.transaction_type == TransactionType.INCOME
    )
    
    if user.role != UserRole.ADMIN:
        income_by_category = income_by_category.filter(Transaction.user_id == user.id)
    
    if start_date:
        income_by_category = income_by_category.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        income_by_category = income_by_category.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    
    income_by_category = income_by_category.group_by(IncomeCategory.name).all()
    
    expense_by_category = db.session.query(
        ExpenseCategory.name,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.transaction_type == TransactionType.EXPENSE
    )
    
    if user.role != UserRole.ADMIN:
        expense_by_category = expense_by_category.filter(Transaction.user_id == user.id)
    
    if start_date:
        expense_by_category = expense_by_category.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        expense_by_category = expense_by_category.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    
    expense_by_category = expense_by_category.group_by(ExpenseCategory.name).all()
    
    return jsonify({
        'income_by_category': [{'category': name, 'amount': float(total)} for name, total in income_by_category],
        'expense_by_category': [{'category': name, 'amount': float(total)} for name, total in expense_by_category],
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    })

# Инициализация тестовых данных
@financial_bp.route('/init-test-data', methods=['POST'])
def init_test_data():
    """Создание тестовых данных для демонстрации"""
    
    # Создание счетов
    accounts_data = [
        {'name': 'Расчетный счет', 'type': AccountType.BANK_ACCOUNT, 'balance': 100000},
        {'name': 'Касса', 'type': AccountType.CASH, 'balance': 50000},
        {'name': 'Корпоративная карта', 'type': AccountType.CARD, 'balance': 75000}
    ]
    
    for acc_data in accounts_data:
        if not Account.query.filter_by(name=acc_data['name']).first():
            account = Account(
                name=acc_data['name'],
                account_type=acc_data['type'],
                initial_balance=acc_data['balance'],
                current_balance=acc_data['balance']
            )
            db.session.add(account)
    
    # Создание категорий доходов
    income_categories = ['Выручка', 'Взнос собственных средств', 'Прочие доходы']
    for cat_name in income_categories:
        if not IncomeCategory.query.filter_by(name=cat_name).first():
            category = IncomeCategory(name=cat_name)
            db.session.add(category)
    
    # Создание категорий расходов
    expense_categories = ['Закупка материалов', 'Зарплата', 'Налоги', 'Аренда', 'Реклама']
    for cat_name in expense_categories:
        if not ExpenseCategory.query.filter_by(name=cat_name).first():
            category = ExpenseCategory(name=cat_name)
            db.session.add(category)
    
    # Создание направлений деятельности
    business_directions = ['Наружка', 'Внутреннее оформление', 'Полиграфия', 'Сувениры', 'Текстиль', 'Печати и штампы', 'Услуги']
    for dir_name in business_directions:
        if not BusinessDirection.query.filter_by(name=dir_name).first():
            direction = BusinessDirection(name=dir_name)
            db.session.add(direction)
    
    db.session.commit()
    
    return jsonify({'message': 'Test data initialized successfully'})

