from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'erp-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== 模型 ====================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), default='个')
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales_reported = db.Column(db.Integer, default=0)  # 销售报量
    factory_prep = db.Column(db.Integer, default=0)    # 工厂备货

class Inbound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(200))
    product = db.relationship('Product', backref='inbounds')

class Outbound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.Column(db.String(100))
    note = db.Column(db.String(200))
    product = db.relationship('Product', backref='outbounds')

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    license_no = db.Column(db.String(100))  # 生产许可证号
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== 初始化数据库 ====================
def init_db():
    with app.app_context():
        db.create_all()
        # 添加示例数据（如果为空）
        if Product.query.count() == 0:
            products = [
                Product(code='P001', name='无线鼠标', unit='个', price=89.0, stock=120, sales_reported=0, factory_prep=0),
                Product(code='P002', name='机械键盘', unit='个', price=299.0, stock=45, sales_reported=0, factory_prep=0),
                Product(code='P003', name='27寸显示器', unit='台', price=1899.0, stock=18, sales_reported=0, factory_prep=0),
                Product(code='P004', name='USB-C 转接头', unit='个', price=29.0, stock=350, sales_reported=0, factory_prep=0),
            ]
            db.session.add_all(products)
            db.session.commit()

# ==================== 路由 ====================
@app.route('/')
def dashboard():
    init_db()
    total_products = Product.query.count()
    total_stock = db.session.query(db.func.sum(Product.stock)).scalar() or 0
    low_stock = Product.query.filter(Product.stock < 20).count()
    recent_inbound = Inbound.query.order_by(Inbound.date.desc()).limit(5).all()
    recent_outbound = Outbound.query.order_by(Outbound.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_products=total_products,
                           total_stock=total_stock,
                           low_stock=low_stock,
                           recent_inbound=recent_inbound,
                           recent_outbound=recent_outbound)

@app.route('/products')
def products():
    init_db()
    all_products = Product.query.order_by(Product.code).all()
    return render_template('products.html', products=all_products)

@app.route('/products/add', methods=['POST'])
def add_product():
    code = request.form.get('code')
    name = request.form.get('name')
    unit = request.form.get('unit', '个')
    price = float(request.form.get('price', 0))
    
    if Product.query.filter_by(code=code).first():
        flash('产品编码已存在！', 'error')
        return redirect(url_for('products'))
    
    new_product = Product(code=code, name=name, unit=unit, price=price, stock=0, sales_reported=0, factory_prep=0)
    db.session.add(new_product)
    db.session.commit()
    flash('产品添加成功！', 'success')
    return redirect(url_for('products'))

@app.route('/stock')
def stock():
    init_db()
    all_products = Product.query.order_by(Product.stock.asc()).all()
    return render_template('stock.html', products=all_products)

@app.route('/inbound')
def inbound_list():
    init_db()
    records = Inbound.query.order_by(Inbound.date.desc()).all()
    products = Product.query.all()
    return render_template('inbound.html', records=records, products=products)

@app.route('/inbound/add', methods=['POST'])
def add_inbound():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    note = request.form.get('note', '')
    
    product = Product.query.get(product_id)
    if not product:
        flash('产品不存在', 'error')
        return redirect(url_for('inbound_list'))
    
    # 更新库存
    product.stock += quantity
    
    new_record = Inbound(product_id=product_id, quantity=quantity, note=note)
    db.session.add(new_record)
    db.session.commit()
    flash(f'入库成功！{product.name} +{quantity}', 'success')
    return redirect(url_for('inbound_list'))

@app.route('/outbound')
def outbound_list():
    init_db()
    records = Outbound.query.order_by(Outbound.date.desc()).all()
    products = Product.query.all()
    return render_template('outbound.html', records=records, products=products)

@app.route('/outbound/add', methods=['POST'])
def add_outbound():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    customer = request.form.get('customer', '')
    note = request.form.get('note', '')
    
    product = Product.query.get(product_id)
    if not product:
        flash('产品不存在', 'error')
        return redirect(url_for('outbound_list'))
    
    if product.stock < quantity:
        flash(f'库存不足！当前库存 {product.stock}', 'error')
        return redirect(url_for('outbound_list'))
    
    # 更新库存
    product.stock -= quantity
    
    new_record = Outbound(product_id=product_id, quantity=quantity, customer=customer, note=note)
    db.session.add(new_record)
    db.session.commit()
    flash(f'出库成功！{product.name} -{quantity}', 'success')
    return redirect(url_for('outbound_list'))


# ==================== 供应商管理 ====================
@app.route('/suppliers')
def suppliers():
    init_db()
    all_suppliers = Supplier.query.order_by(Supplier.created_at.desc()).all()
    return render_template('suppliers.html', suppliers=all_suppliers)

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    name = request.form.get('name')
    address = request.form.get('address', '')
    license_no = request.form.get('license_no', '')
    
    new_supplier = Supplier(name=name, address=address, license_no=license_no)
    db.session.add(new_supplier)
    db.session.commit()
    flash(f'供应商 {name} 添加成功！', 'success')
    return redirect(url_for('suppliers'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)