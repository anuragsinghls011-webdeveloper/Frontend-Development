from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import mysql.connector
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'meditrack_secret_key'

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'thakur',
    'password': 'rohitls',
    'database': 'hospital'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.errors.ProgrammingError as e:
        if "Unknown database" in str(e):
            temp_config = MYSQL_CONFIG.copy()
            db_name = temp_config.pop("database")
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.close()
            conn.close()
            return mysql.connector.connect(**MYSQL_CONFIG)
        else:
            raise

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS equipment")
    cursor.execute("DROP TABLE IF EXISTS medicines")
    cursor.execute("DROP TABLE IF EXISTS general_surgery_equipments")

    cursor.execute('''
        CREATE TABLE equipment (
            equipment_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            manufacturer VARCHAR(255) NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            location VARCHAR(255) DEFAULT 'Unknown',
            last_maintenance DATE NOT NULL,
            next_maintenance DATE NOT NULL,
            status VARCHAR(100) DEFAULT 'Operational',
            date_added DATE DEFAULT (CURRENT_DATE)
        )
    ''')

    cursor.execute('''
        CREATE TABLE medicines (
            medicine_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            manufacturer VARCHAR(255) NOT NULL,
            quantity INT NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            expiry_date DATE NOT NULL,
            date_added DATE DEFAULT (CURRENT_DATE)
        )
    ''')

    cursor.execute('''
        CREATE TABLE general_surgery_equipments (
            equipment_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            manufacturer VARCHAR(255) NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            last_maintenance DATE NOT NULL,
            next_maintenance DATE NOT NULL,
            quantity INT NOT NULL,
            type VARCHAR(255) NOT NULL,
            date_added DATE DEFAULT (CURRENT_DATE)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("MySQL database initialized successfully!")


def add_sample_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO equipment (name, manufacturer, cost, location, last_maintenance, next_maintenance)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ('X-Ray Machine', 'Siemens', 50000.00, 'Radiology', '2024-12-01', '2025-06-01'))

    cursor.execute("""
        INSERT INTO medicines (name, manufacturer, quantity, cost, expiry_date)
        VALUES (%s, %s, %s, %s, %s)
    """, ('Paracetamol', 'GSK', 100, 5.99, '2025-12-31'))

    cursor.execute("""
        INSERT INTO general_surgery_equipments (name, manufacturer, cost, last_maintenance, next_maintenance, quantity, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, ('Surgical Scissors', 'Medtronic', 129.99, '2024-11-15', '2025-05-15', 50, 'Cutting'))

    conn.commit()
    cursor.close()
    conn.close()

def is_valid_number(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def is_valid_date(date_string):
    try:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
            return False
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("SELECT COUNT(*) as count FROM equipment")
    total_equipment = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM medicines")
    total_medicines = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM general_surgery_equipments")
    total_surgery_equipment = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count FROM medicines
        WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    """)
    expiring_med_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count FROM equipment
        WHERE next_maintenance <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    """)
    maintenance_due_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM medicines WHERE quantity <= 5")
    low_stock_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM general_surgery_equipments WHERE quantity <= 5")
    low_stock_count += cursor.fetchone()['count']

    alert_count = expiring_med_count + maintenance_due_count + low_stock_count

    cursor.execute("""
        SELECT * FROM medicines
        WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY expiry_date
    """)
    expiring_medicines = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM equipment
        WHERE next_maintenance <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        ORDER BY next_maintenance
    """)
    maintenance_equipment = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        equipment_count=total_equipment,
        medicine_count=total_medicines,
        surgery_count=total_surgery_equipment,
        alert_count=alert_count,
        expiring_medicines=expiring_medicines,
        maintenance_equipment=maintenance_equipment
    )

@app.route('/equipment', methods=['GET', 'POST'])
def equipment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.form
        cursor.execute("SELECT 1 FROM equipment WHERE equipment_id = %s", (data['equipment_id'],))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("""
                INSERT INTO equipment (equipment_id, name, manufacturer, cost, location, last_maintenance, next_maintenance, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['equipment_id'], data['name'], data['manufacturer'], data['cost'],
                data.get('location', 'Unknown'), data['last_maintenance'],
                data['next_maintenance'], data.get('status', 'Operational')
            ))
            conn.commit()
            flash('Equipment added successfully!', 'success')
        else:
            flash('Equipment ID already exists!', 'danger')
        cursor.close()
        conn.close()
        return redirect('/equipment')

    search = request.args.get('search', '')
    search_by = request.args.get('search_by', 'name')

    if search:
        if search_by == 'id':
            cursor.execute("SELECT * FROM equipment WHERE equipment_id = %s", (search,))
            rows = cursor.fetchall()
        else:
            pattern = f"%{search.lower()}%"
            cursor.execute("""
                SELECT * FROM equipment
                WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s
            """, (pattern, pattern))
            rows = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM equipment")
        rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("equipment.html", rows=rows, search=search, search_by=search_by)

@app.route('/medicines', methods=['GET', 'POST'])
def medicines():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.form
        cursor.execute("SELECT 1 FROM medicines WHERE medicine_id = %s", (data['medicine_id'],))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("""
                INSERT INTO medicines (medicine_id, name, manufacturer, quantity, cost, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['medicine_id'], data['name'], data['manufacturer'],
                data['quantity'], data['cost'], data['expiry_date']
            ))
            conn.commit()
            flash('Medicine added successfully!', 'success')
        else:
            flash('Medicine ID already exists!', 'danger')
        cursor.close()
        conn.close()
        return redirect('/medicines')

    search = request.args.get('search', '')
    search_by = request.args.get('search_by', 'name')

    if search:
        if search_by == 'id':
            cursor.execute("SELECT * FROM medicines WHERE medicine_id = %s", (search,))
            rows = cursor.fetchall()
        else:
            pattern = f"%{search.lower()}%"
            cursor.execute("""
                SELECT * FROM medicines
                WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s
            """, (pattern, pattern))
            rows = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM medicines")
        rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("medicines.html", rows=rows, search=search, search_by=search_by)

@app.route('/general_surgery', methods=['GET', 'POST'])
def general_surgery():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.form
        cursor.execute("SELECT 1 FROM general_surgery_equipments WHERE equipment_id = %s", (data['equipment_id'],))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("""
                INSERT INTO general_surgery_equipments (equipment_id, name, manufacturer, cost, last_maintenance, next_maintenance, quantity, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['equipment_id'], data['name'], data['manufacturer'], data['cost'],
                data['last_maintenance'], data['next_maintenance'],
                data['quantity'], data['type']
            ))
            conn.commit()
            flash('Surgery equipment added successfully!', 'success')
        else:
            flash('Equipment ID already exists!', 'danger')
        cursor.close()
        conn.close()
        return redirect('/general_surgery')

    search = request.args.get('search', '')
    search_by = request.args.get('search_by', 'name')

    if search:
        if search_by == 'id':
            cursor.execute("SELECT * FROM general_surgery_equipments WHERE equipment_id = %s", (search,))
            rows = cursor.fetchall()
        else:
            pattern = f"%{search.lower()}%"
            cursor.execute("""
                SELECT * FROM general_surgery_equipments
                WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s
            """, (pattern, pattern))
            rows = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM general_surgery_equipments")
        rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("general_surgery.html", rows=rows, search=search, search_by=search_by)

@app.route('/update_equipments/<int:equipment_id>', methods=['POST'])
def update_equipment(equipment_id):
    field = request.form.get('field')
    value = request.form.get('value')
    allowed_fields = ['name', 'manufacturer', 'cost', 'location', 'last_maintenance', 'next_maintenance', 'status']
    if field not in allowed_fields:
        return jsonify({"success": False, "error": f"Invalid field: {field}"})
    if field == 'cost' and not is_valid_number(value):
        return jsonify({"success": False, "error": f"{field} must be a number"})
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE equipment SET {field} = %s WHERE equipment_id = %s"
        cursor.execute(query, (value, equipment_id))
        conn.commit()
        cursor.execute("SELECT * FROM equipment WHERE equipment_id = %s", (equipment_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Equipment not found after update"})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/update_medicine/<int:medicine_id>', methods=['POST'])
def update_medicine(medicine_id):
    field = request.form.get('field')
    value = request.form.get('value')
    allowed_fields = ['name', 'manufacturer', 'quantity', 'cost', 'expiry_date']
    if field not in allowed_fields:
        return jsonify({"success": False, "error": f"Invalid field: {field}"})
    if field in ['quantity', 'cost'] and not is_valid_number(value):
        return jsonify({"success": False, "error": f"{field} must be a number"})
    if field == 'expiry_date' and not is_valid_date(value):
        return jsonify({"success": False, "error": "Invalid date format"})
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE medicines SET {field} = %s WHERE medicine_id = %s"
        cursor.execute(query, (value, medicine_id))
        conn.commit()
        cursor.execute("SELECT * FROM medicines WHERE medicine_id = %s", (medicine_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Medicine not found after update"})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/update_general_surgerys/<int:equipment_id>', methods=['POST'])
def update_general_surgery(equipment_id):
    field = request.form.get('field')
    value = request.form.get('value')
    allowed_fields = ['name', 'manufacturer', 'cost', 'last_maintenance', 'next_maintenance', 'quantity', 'type']
    if field not in allowed_fields:
        return jsonify({"success": False, "error": f"Invalid field: {field}"})
    if field in ['quantity', 'cost'] and not is_valid_number(value):
        return jsonify({"success": False, "error": f"{field} must be a number"})
    if field in ['last_maintenance', 'next_maintenance'] and not is_valid_date(value):
        return jsonify({"success": False, "error": "Invalid date format"})
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE general_surgery_equipments SET {field} = %s WHERE equipment_id = %s"
        cursor.execute(query, (value, equipment_id))
        conn.commit()
        cursor.execute("SELECT * FROM general_surgery_equipments WHERE equipment_id = %s", (equipment_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Surgery equipment not found after update"})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/alerts')
def alerts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("""
        SELECT *, DATEDIFF(expiry_date, CURDATE()) AS days_until_expiry 
        FROM medicines 
        WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY expiry_date
    """)
    expiring_medicines = cursor.fetchall()

    cursor.execute("""
        SELECT *, DATEDIFF(next_maintenance, CURDATE()) AS days_until_maintenance 
        FROM equipment 
        WHERE next_maintenance <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        ORDER BY next_maintenance
    """)
    maintenance_equipment = cursor.fetchall()

    low_stock_items = []

    cursor.execute("""
        SELECT medicine_id as id, name, 'medicines' as type, quantity, cost, manufacturer, expiry_date
        FROM medicines WHERE quantity <= 5
        ORDER BY quantity ASC
    """)
    low_stock_items.extend(cursor.fetchall())

    cursor.execute("""
        SELECT equipment_id as id, name, 'general_surgery' as type, quantity, cost, manufacturer, next_maintenance
        FROM general_surgery_equipments WHERE quantity <= 5
        ORDER BY quantity ASC
    """)
    low_stock_items.extend(cursor.fetchall())

    alert_count = len(expiring_medicines) + len(maintenance_equipment) + len(low_stock_items)

    cursor.close()
    conn.close()

    return render_template(
        "alerts.html",
        expiring_medicines=expiring_medicines,
        maintenance_equipment=maintenance_equipment,
        low_stock_items=low_stock_items,
        alert_count=alert_count
    )

@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    today = datetime.now().strftime('%Y-%m-%d')

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', today)
    report_type = request.args.get('report_type', 'all')

    date_condition = ""
    if start_date and end_date:
        date_condition = f" AND date_added BETWEEN '{start_date}' AND '{end_date}'"

    total_equipment = equipment_value = 0
    total_medicines = medicines_value = 0
    total_surgery = surgery_value = 0

    if report_type in ['all', 'equipment']:
        cursor.execute(f"SELECT COUNT(*) as count, SUM(cost) as value FROM equipment WHERE 1=1 {date_condition}")
        res = cursor.fetchone()
        total_equipment = res['count'] or 0
        equipment_value = res['value'] or 0

    if report_type in ['all', 'medicines']:
        cursor.execute(f"SELECT COUNT(*) as count, SUM(cost * quantity) as value FROM medicines WHERE 1=1 {date_condition}")
        res = cursor.fetchone()
        total_medicines = res['count'] or 0
        medicines_value = res['value'] or 0

    if report_type in ['all', 'general_surgery']:
        cursor.execute(f"SELECT COUNT(*) as count, SUM(cost * quantity) as value FROM general_surgery_equipments WHERE 1=1 {date_condition}")
        res = cursor.fetchone()
        total_surgery = res['count'] or 0
        surgery_value = res['value'] or 0

    total_items = total_equipment + total_medicines + total_surgery
    total_value = round(equipment_value + medicines_value + surgery_value, 2)

    detailed_data = []

    if report_type in ['all', 'equipment']:
        cursor.execute(f"""
            SELECT 'equipment' as type, equipment_id as id, name, manufacturer, cost, location, status, date_added
            FROM equipment WHERE 1=1 {date_condition} ORDER BY equipment_id DESC
        """)
        detailed_data.extend(cursor.fetchall())

    if report_type in ['all', 'medicines']:
        cursor.execute(f"""
            SELECT 'medicine' as type, medicine_id as id, name, manufacturer, cost, quantity, expiry_date, date_added
            FROM medicines WHERE 1=1 {date_condition} ORDER BY medicine_id DESC
        """)
        detailed_data.extend(cursor.fetchall())

    if report_type in ['all', 'general_surgery']:
        cursor.execute(f"""
            SELECT 'surgery' as type, equipment_id as id, name, manufacturer, cost, quantity, type as item_type, date_added
            FROM general_surgery_equipments WHERE 1=1 {date_condition} ORDER BY equipment_id DESC
        """)
        detailed_data.extend(cursor.fetchall())

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        start_date=start_date,
        end_date=end_date,
        report_type=report_type,
        today=today,
        total_items=total_items,
        total_value=total_value,
        equipment_count=total_equipment,
        medicines_count=total_medicines,
        surgery_count=total_surgery,
        equipment_value=round(equipment_value, 2),
        medicines_value=round(medicines_value, 2),
        surgery_value=round(surgery_value, 2),
        detailed_data=detailed_data
    )

@app.route('/debug')
def debug():
    return jsonify({
        "status": "ok",
        "message": "Flask application is working correctly",
        "routes": [
            "/update_equipments/<int:equipment_id>",
            "/update_medicine/<int:medicine_id>",
            "/update_general_surgerys/<int:equipment_id>"
        ]
    })

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    if not query:
        return redirect('/dashboard')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    pattern = f"%{query}%"
    cursor.execute("""
        SELECT *, 'equipment' as type FROM equipment
        WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s OR CAST(equipment_id AS CHAR) LIKE %s
    """, (pattern, pattern, pattern))
    equipment_results = cursor.fetchall()

    cursor.execute("""
        SELECT *, 'medicine' as type FROM medicines
        WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s OR CAST(medicine_id AS CHAR) LIKE %s
    """, (pattern, pattern, pattern))
    medicine_results = cursor.fetchall()

    cursor.execute("""
        SELECT *, 'surgery' as type FROM general_surgery_equipments
        WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s OR CAST(equipment_id AS CHAR) LIKE %s
    """, (pattern, pattern, pattern))
    surgery_results = cursor.fetchall()

    results = equipment_results + medicine_results + surgery_results

    cursor.close()
    conn.close()

    return render_template(
        "search_results.html",
        query=query,
        results=results,
        result_count=len(results),
        equipment_count=len(equipment_results),
        medicine_count=len(medicine_results),
        surgery_count=len(surgery_results),
        total_count=len(results)
    )

@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('query', '').lower()
    if not query or len(query) < 2:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    pattern = f"%{query}%"

    cursor.execute("""
        SELECT name, 'equipment' as type FROM equipment
        WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s
        LIMIT 5
    """, (pattern, pattern))
    equipment = cursor.fetchall()

    cursor.execute("""
        SELECT name, 'medicine' as type FROM medicines
        WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s
        LIMIT 5
    """, (pattern, pattern))
    medicines = cursor.fetchall()

    cursor.execute("""
        SELECT name, 'surgery' as type FROM general_surgery_equipments
        WHERE LOWER(name) LIKE %s OR LOWER(manufacturer) LIKE %s
        LIMIT 5
    """, (pattern, pattern))
    surgery = cursor.fetchall()

    suggestions = equipment + medicines + surgery

    cursor.close()
    conn.close()

    return jsonify(suggestions)

if __name__ == '__main__':
    if not os.path.exists('initialized.flag'):
        init_db()
        add_sample_data()
        open('initialized.flag', 'w').close()
    print("Flask app started. All routes registered.")
    app.run(debug=True)