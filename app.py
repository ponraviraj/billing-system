from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
DATABASE = 'billing.db'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_id TEXT UNIQUE NOT NULL,
            available_stocks INTEGER NOT NULL,
            price REAL NOT NULL,
            tax_percentage REAL NOT NULL
        )
    ''')
    
    # Create Purchases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT NOT NULL,
            purchase_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            tax_amount REAL NOT NULL,
            paid_amount REAL NOT NULL,
            balance_amount REAL NOT NULL,
            items_json TEXT NOT NULL,
            balance_denominations TEXT
        )
    ''')
    
    # Create Shop Denominations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_denominations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value INTEGER UNIQUE NOT NULL,
            count INTEGER NOT NULL DEFAULT 0
        )
    ''')
    
    # Seed products if empty
    cursor.execute('SELECT COUNT(*) as count FROM products')
    if cursor.fetchone()[0] == 0:
        products = [
            ("Laptop", "P001", 10, 50000.00, 18.0),
            ("Mouse", "P002", 50, 500.00, 12.0),
            ("Keyboard", "P003", 30, 1500.00, 12.0),
            ("Monitor", "P004", 15, 15000.00, 18.0),
            ("USB Cable", "P005", 100, 200.00, 5.0),
        ]
        cursor.executemany(
            'INSERT INTO products (name, product_id, available_stocks, price, tax_percentage) VALUES (?, ?, ?, ?, ?)',
            products
        )
    
    # Remove old denominations (2000, 200, 100) if they exist
    cursor.execute('DELETE FROM shop_denominations WHERE value IN (2000, 200, 100)')
    
    # Seed denominations if empty (as per image: 500, 50, 20, 10, 5, 2, 1)
    cursor.execute('SELECT COUNT(*) as count FROM shop_denominations')
    if cursor.fetchone()[0] == 0:
        denominations = [(500, 50), (50, 50), (20, 50), (10, 50), (5, 50), (2, 50), (1, 50)]
        cursor.executemany(
            'INSERT INTO shop_denominations (value, count) VALUES (?, ?)',
            denominations
        )
    else:
        # Ensure only correct denominations exist, add missing ones
        existing_values = [row[0] for row in cursor.execute('SELECT value FROM shop_denominations').fetchall()]
        correct_denominations = [500, 50, 20, 10, 5, 2, 1]
        for denom_value in correct_denominations:
            if denom_value not in existing_values:
                cursor.execute(
                    'INSERT INTO shop_denominations (value, count) VALUES (?, ?)',
                    (denom_value, 50)
                )
    
    conn.commit()
    conn.close()

# Helper function to calculate balance denominations
def calculate_balance_denominations(balance):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value, count FROM shop_denominations ORDER BY value DESC')
    denominations = cursor.fetchall()
    
    result = []
    remaining = int(balance)
    
    for denom in denominations:
        value, count = denom['value'], denom['count']
        if remaining >= value and count > 0:
            notes_needed = min(remaining // value, count)
            if notes_needed > 0:
                result.append({"value": value, "count": notes_needed})
                remaining -= notes_needed * value
    
    conn.close()
    return result, remaining == 0

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    denominations = conn.execute('SELECT * FROM shop_denominations ORDER BY value DESC').fetchall()
    conn.close()
    return render_template('page1.html', products=products, denominations=denominations)

@app.route('/calculate_preview', methods=['POST'])
def calculate_preview():
    """Calculate bill total without saving to database - for preview"""
    try:
        data = request.json
        items = data['items']
        
        conn = get_db_connection()
        
        subtotal = 0
        total_tax = 0
        item_details = []
        
        for item in items:
            product = conn.execute(
                'SELECT * FROM products WHERE product_id = ?', 
                (item['product_id'],)
            ).fetchone()
            
            if not product:
                conn.close()
                return jsonify({'error': f"Product {item['product_id']} not found"}), 400
            
            quantity = int(item['quantity'])
            item_price = product['price'] * quantity
            item_tax = (item_price * product['tax_percentage']) / 100
            
            item_details.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'quantity': quantity,
                'price': product['price'],
                'item_total': item_price,
                'item_tax': item_tax
            })
            
            subtotal += item_price
            total_tax += item_tax
        
        total_amount = subtotal + total_tax
        rounded_down_total = int(total_amount)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'subtotal': subtotal,
            'total_tax': total_tax,
            'total_amount': total_amount,
            'rounded_down_total': rounded_down_total,
            'items': item_details
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    try:
        data = request.json
        customer_email = data['customer_email']
        items = data['items']
        paid_amount = float(data['paid_amount'])
        denomination_counts = data['denomination_counts']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate bill
        bill_items = []
        subtotal = 0
        total_tax = 0
        
        for item in items:
            product = conn.execute(
                'SELECT * FROM products WHERE product_id = ?', 
                (item['product_id'],)
            ).fetchone()
            
            if not product:
                conn.close()
                return jsonify({'error': f"Product {item['product_id']} not found"}), 400
            
            quantity = int(item['quantity'])
            if product['available_stocks'] < quantity:
                conn.close()
                return jsonify({'error': f"Insufficient stock for {product['name']}"}), 400
            
            item_price = product['price'] * quantity
            item_tax = (item_price * product['tax_percentage']) / 100
            
            bill_items.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'quantity': quantity,
                'price': product['price'],
                'tax_percentage': product['tax_percentage'],
                'item_total': item_price,
                'item_tax': item_tax
            })
            
            subtotal += item_price
            total_tax += item_tax
            
            # Update stock
            cursor.execute(
                'UPDATE products SET available_stocks = available_stocks - ? WHERE product_id = ?',
                (quantity, product['product_id'])
            )
        
        total_amount = subtotal + total_tax
        # Rounded down value as per requirement
        rounded_down_total = int(total_amount)
        balance_amount = paid_amount - rounded_down_total
        
        if balance_amount < 0:
            conn.close()
            return jsonify({
                'error': f'Insufficient payment. Total bill amount is ₹{rounded_down_total:.2f}, but you paid only ₹{paid_amount:.2f}. Please pay ₹{abs(balance_amount):.2f} more.'
            }), 400
        
        # Calculate balance denominations
        balance_denoms, can_give_exact = calculate_balance_denominations(balance_amount)
        
        if not can_give_exact and balance_amount > 0:
            conn.close()
            return jsonify({
                'error': f'Cannot provide exact change. Balance is ₹{balance_amount:.2f}, but we cannot provide this amount with available denominations.'
            }), 400
        
        # Update shop denominations
        for denom_update in denomination_counts:
            cursor.execute(
                'UPDATE shop_denominations SET count = count + ? WHERE value = ?',
                (denom_update['count'], denom_update['value'])
            )
        
        for denom in balance_denoms:
            cursor.execute(
                'UPDATE shop_denominations SET count = count - ? WHERE value = ?',
                (denom['count'], denom['value'])
            )
        
        # Save purchase (store rounded down total as balance is calculated from it)
        purchase_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO purchases 
            (customer_email, purchase_date, total_amount, tax_amount, paid_amount, balance_amount, items_json, balance_denominations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_email,
            purchase_date,
            rounded_down_total,
            total_tax,
            paid_amount,
            balance_amount,
            json.dumps(bill_items),
            json.dumps(balance_denoms)
        ))
        
        purchase_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'purchase_id': purchase_id,
            'items': bill_items,
            'subtotal': subtotal,
            'tax': total_tax,
            'total': total_amount,
            'rounded_down_total': rounded_down_total,
            'paid': paid_amount,
            'balance': balance_amount,
            'balance_denominations': balance_denoms
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bill/<int:purchase_id>')
def view_bill(purchase_id):
    conn = get_db_connection()
    purchase = conn.execute('SELECT * FROM purchases WHERE id = ?', (purchase_id,)).fetchone()
    conn.close()
    
    if not purchase:
        return "Purchase not found", 404
    
    items = json.loads(purchase['items_json'])
    balance_denoms = json.loads(purchase['balance_denominations']) if purchase['balance_denominations'] else []
    
    # Calculate values for display
    subtotal = sum(item['item_total'] for item in items)
    total_tax = sum(item['item_tax'] for item in items)
    net_total = subtotal + total_tax
    rounded_down = int(net_total)
    balance = purchase['balance_amount']
    
    return render_template('page2.html', 
                         purchase=purchase, 
                         items=items, 
                         balance_denominations=balance_denoms,
                         subtotal=subtotal,
                         total_tax=total_tax,
                         net_total=net_total,
                         rounded_down=rounded_down,
                         balance=balance)

@app.route('/purchases/<email>')
def customer_purchases(email):
    conn = get_db_connection()
    purchases_raw = conn.execute(
        'SELECT * FROM purchases WHERE customer_email = ? ORDER BY purchase_date DESC', 
        (email,)
    ).fetchall()
    conn.close()
    
    # Parse items_json for each purchase
    purchases = []
    for purchase in purchases_raw:
        purchase_dict = dict(purchase)
        purchase_dict['items_list'] = json.loads(purchase['items_json'])
        purchases.append(purchase_dict)
    
    return render_template('purchases.html', email=email, purchases=purchases)

@app.route('/purchase_details/<int:purchase_id>')
def purchase_details(purchase_id):
    conn = get_db_connection()
    purchase = conn.execute('SELECT * FROM purchases WHERE id = ?', (purchase_id,)).fetchone()
    conn.close()
    
    if not purchase:
        return jsonify({'error': 'Purchase not found'}), 404
    
    items = json.loads(purchase['items_json'])
    return jsonify({'items': items})

@app.route('/admin/products')
def admin_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY product_id').fetchall()
    conn.close()
    return render_template('admin_products.html', products=products)

@app.route('/admin/products/add', methods=['POST'])
def add_product():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, product_id, available_stocks, price, tax_percentage)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['product_id'],
            int(data['available_stocks']),
            float(data['price']),
            float(data['tax_percentage'])
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Product added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/products/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET name = ?, available_stocks = ?, price = ?, tax_percentage = ?
            WHERE id = ?
        ''', (
            data['name'],
            int(data['available_stocks']),
            float(data['price']),
            float(data['tax_percentage']),
            product_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Product updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)