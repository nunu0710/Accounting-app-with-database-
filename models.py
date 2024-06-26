from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'sale' or 'purchase'

class AccountBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False)

    @classmethod
    def get_balance(cls):
        balance_record = cls.query.first()
        if not balance_record:
            balance_record = cls(balance=0.0)
            db.session.add(balance_record)
            db.session.commit()
        return balance_record

    def update_balance(self, amount):
        self.balance += amount
        db.session.commit()
