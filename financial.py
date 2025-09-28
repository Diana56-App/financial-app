from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class AccountType(Enum):
    BANK_ACCOUNT = "bank_account"
    CARD = "card"
    CASH = "cash"
    ROBOKASSA = "robokassa"
    OTHER = "other"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.MANAGER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    planned_transactions = db.relationship('PlannedTransaction', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat()
        }

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    initial_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    current_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='RUB')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type.value,
            'initial_balance': float(self.initial_balance),
            'current_balance': float(self.current_balance),
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class IncomeCategory(db.Model):
    __tablename__ = 'income_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('income_categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Самосвязь для иерархии
    children = db.relationship('IncomeCategory', backref=db.backref('parent', remote_side=[id]))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Самосвязь для иерархии
    children = db.relationship('ExpenseCategory', backref=db.backref('parent', remote_side=[id]))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class BusinessDirection(db.Model):
    __tablename__ = 'business_directions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    income_category_id = db.Column(db.Integer, db.ForeignKey('income_categories.id'), nullable=True)
    expense_category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=True)
    business_direction_id = db.Column(db.Integer, db.ForeignKey('business_directions.id'), nullable=True)
    
    # Связи
    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    to_account = db.relationship('Account', foreign_keys=[to_account_id])
    income_category = db.relationship('IncomeCategory')
    expense_category = db.relationship('ExpenseCategory')
    business_direction = db.relationship('BusinessDirection')

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type.value,
            'amount': float(self.amount),
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'income_category_id': self.income_category_id,
            'expense_category_id': self.expense_category_id,
            'business_direction_id': self.business_direction_id,
            'from_account': self.from_account.to_dict() if self.from_account else None,
            'to_account': self.to_account.to_dict() if self.to_account else None,
            'income_category': self.income_category.to_dict() if self.income_category else None,
            'expense_category': self.expense_category.to_dict() if self.expense_category else None,
            'business_direction': self.business_direction.to_dict() if self.business_direction else None
        }

class PlannedTransaction(db.Model):
    __tablename__ = 'planned_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    planned_date = db.Column(db.DateTime, nullable=False)
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    recurrence_pattern = db.Column(db.String(50))  # daily, weekly, monthly, yearly
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    income_category_id = db.Column(db.Integer, db.ForeignKey('income_categories.id'), nullable=True)
    expense_category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=True)
    business_direction_id = db.Column(db.Integer, db.ForeignKey('business_directions.id'), nullable=True)
    
    # Связи
    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    to_account = db.relationship('Account', foreign_keys=[to_account_id])
    income_category = db.relationship('IncomeCategory')
    expense_category = db.relationship('ExpenseCategory')
    business_direction = db.relationship('BusinessDirection')
    completed_transaction = db.relationship('Transaction')

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type.value,
            'amount': float(self.amount),
            'description': self.description,
            'planned_date': self.planned_date.isoformat(),
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'is_completed': self.is_completed,
            'completed_transaction_id': self.completed_transaction_id,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'income_category_id': self.income_category_id,
            'expense_category_id': self.expense_category_id,
            'business_direction_id': self.business_direction_id
        }

