from flask import Flask, render_template, request, redirect, flash
from models import db, Transaction, AccountBalance, InventoryItem
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    inventory = InventoryItem.query.all()
    return render_template('index.html', inventory=inventory)

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    balance_record = AccountBalance.get_balance()
    if request.method == 'POST':
        command = request.form['command']
        amount = float(request.form['amount'])
        if command == 'add':
            balance_record.update_balance(amount)
        elif command == 'subtract':
            balance_record.update_balance(-amount)
        return redirect('/balance')
    return render_template('balance.html', balance=balance_record.balance)

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'POST':
        item_name = request.form['item_name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        total = price * quantity

        # Check if the item exists in the inventory
        inventory_item = InventoryItem.query.filter_by(item_name=item_name).first()
        if inventory_item:
            if inventory_item.quantity < quantity:
                flash("Error: Not enough inventory to complete the sale.")
                return redirect('/sales')
            else:
                inventory_item.quantity -= quantity
                if inventory_item.quantity == 0:
                    db.session.delete(inventory_item)
        else:
            flash("Error: Item not found in inventory.")
            return redirect('/sales')

        # Record the sale transaction
        new_sale = Transaction(type='sale', item_name=item_name, price=price, quantity=quantity, total=total, time=datetime.datetime.utcnow())
        db.session.add(new_sale)
        db.session.commit()

        # Update balance
        balance_record = AccountBalance.get_balance()
        balance_record.update_balance(total)
        return redirect('/sales')
    return render_template('sales.html')

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        item_name = request.form['item_name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        total = price * quantity

        # Check if there is enough balance to make the purchase
        balance_record = AccountBalance.get_balance()
        if balance_record.balance < total:
            flash("Error: Not enough money to complete the purchase.")
            return redirect('/purchase')

        # Check if the item exists in the inventory
        inventory_item = InventoryItem.query.filter_by(item_name=item_name).first()
        if inventory_item:
            inventory_item.quantity += quantity
        else:
            new_inventory_item = InventoryItem(item_name=item_name, price=price, quantity=quantity)
            db.session.add(new_inventory_item)

        # Record the purchase transaction
        new_purchase = Transaction(type='purchase', item_name=item_name, price=price, quantity=quantity, total=total, time=datetime.datetime.utcnow())
        db.session.add(new_purchase)
        db.session.commit()

        # Update balance
        balance_record.update_balance(-total)
        return redirect('/purchase')
    return render_template('purchase.html')

@app.route('/history')
def history():
    sales_history = Transaction.query.filter_by(type='sale').all()
    purchase_history = Transaction.query.filter_by(type='purchase').all()
    return render_template('history.html', sales_history=sales_history, purchase_history=purchase_history)

if __name__ == '__main__':
    app.run(debug=True)
