# -*- coding: utf-8 -*-
"""
Flask API Server - Serves Vue.js UI and connects to Python backend
"""
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime

from src.services.customer_service import CustomerService
from src.services.product_service import ProductService
from src.services.order_service import OrderService
from src.services.debt_service import DebtService
from src.services.excel_service import ExcelService


def create_api_server(db, port=5000):
    """Create Flask API server"""
    app = Flask(__name__, 
                static_folder='js',
                static_url_path='/js',
                template_folder='.')
    CORS(app)
    
    # Initialize services
    customer_service = CustomerService(db)
    product_service = ProductService(db)
    order_service = OrderService(db)
    debt_service = DebtService(db)
    excel_service = ExcelService()
    
    @app.route('/')
    def index():
        """Main dashboard"""
        return render_template_string(load_vue_page('Dashboard'))
    
    @app.route('/b2b-orders')
    def b2b_orders():
        """B2B Orders page"""
        return render_template_string(load_vue_page('B2BOrders/Index'))
    
    @app.route('/debts')
    def debts():
        """Debts page"""
        return render_template_string(load_vue_page('Debts/Index'))
    
    @app.route('/customers')
    def customers():
        """Customers page"""
        return render_template_string(load_vue_page('Customers/Index'))
    
    @app.route('/products')
    def products():
        """Products page"""
        return render_template_string(load_vue_page('Products/Index'))
    
    # ── API Endpoints ─────────────────────────────────────────────────────────
    
    @app.route('/api/dashboard')
    def api_dashboard():
        """Dashboard statistics"""
        order_stats = order_service.get_stats()
        debt_stats = debt_service.get_stats()
        customer_stats = customer_service.get_stats()
        
        return jsonify({
            'allTimeStats': {
                'total_orders': order_stats['total_orders'],
                'total_revenue': order_stats['total_revenue'],
                'total_profit': order_stats['total_profit'],
                'total_debt_count': debt_stats['count_pending'] + debt_stats['count_partial'],
                'total_debt_amount': debt_stats['total_remaining'],
            },
            'periodStats': {
                'revenue': order_stats['total_revenue'],
                'orders': order_stats['total_orders'],
                'new_customers': customer_stats['total_customers'],
                'avg_order_value': order_stats['total_revenue'] / max(order_stats['total_orders'], 1),
            },
        })
    
    @app.route('/api/b2b-orders')
    def api_b2b_orders():
        """Get B2B orders"""
        search = request.args.get('search', '')
        from_date = request.args.get('from', '')
        to_date = request.args.get('to', '')
        
        orders = order_service.get_all(
            search=search,
            from_date=from_date,
            to_date=to_date
        )
        
        stats = order_service.get_stats()
        
        return jsonify({
            'data': orders,
            'stats': stats,
            'total': len(orders),
        })
    
    @app.route('/api/b2b-orders/<int:order_id>')
    def api_b2b_order_detail(order_id):
        """Get single order detail"""
        order = order_service.get_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        return jsonify(order)
    
    @app.route('/api/b2b-orders', methods=['POST'])
    def api_create_b2b_order():
        """Create new B2B order"""
        data = request.json
        items = data.get('items', [])
        
        order_id = order_service.create(data, items)
        order = order_service.get_by_id(order_id)
        
        return jsonify(order), 201
    
    @app.route('/api/b2b-orders/<int:order_id>', methods=['PUT'])
    def api_update_b2b_order(order_id):
        """Update B2B order"""
        data = request.json
        items = data.get('items', [])
        
        order_service.update(order_id, data, items)
        order = order_service.get_by_id(order_id)
        
        return jsonify(order)
    
    @app.route('/api/b2b-orders/<int:order_id>', methods=['DELETE'])
    def api_delete_b2b_order(order_id):
        """Delete B2B order"""
        order_service.delete(order_id)
        return jsonify({'success': True})
    
    @app.route('/api/debts')
    def api_debts():
        """Get debts"""
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        debts = debt_service.get_all(search=search, status=status)
        stats = debt_service.get_stats()
        
        return jsonify({
            'data': debts,
            'stats': stats,
            'total': len(debts),
        })
    
    @app.route('/api/debts/<int:debt_id>')
    def api_debt_detail(debt_id):
        """Get debt detail"""
        debt = debt_service.get_by_id(debt_id)
        if not debt:
            return jsonify({'error': 'Debt not found'}), 404
        return jsonify(debt)
    
    @app.route('/api/debts/<int:debt_id>/payments', methods=['POST'])
    def api_add_debt_payment(debt_id):
        """Add payment to debt"""
        data = request.json
        
        try:
            payment_id = debt_service.add_payment(debt_id, data)
            debt = debt_service.get_by_id(debt_id)
            return jsonify(debt), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/customers')
    def api_customers():
        """Get customers"""
        search = request.args.get('search', '')
        customers = customer_service.get_all(search=search)
        
        return jsonify({
            'data': customers,
            'total': len(customers),
        })
    
    @app.route('/api/customers', methods=['POST'])
    def api_create_customer():
        """Create new customer"""
        data = request.json
        customer_id = customer_service.create(data)
        customer = customer_service.get_by_id(customer_id)
        
        return jsonify(customer), 201
    
    @app.route('/api/products')
    def api_products():
        """Get products"""
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)
        
        products = product_service.get_all(search=search, category_id=category_id)
        
        return jsonify({
            'data': products,
            'total': len(products),
        })
    
    @app.route('/api/import-excel', methods=['POST'])
    def api_import_excel():
        """Import orders from Excel"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        upload_path = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(upload_path)
        
        try:
            result = excel_service.import_orders_from_excel(upload_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/export-order/<int:order_id>')
    def api_export_order(order_id):
        """Export order to Excel"""
        order = order_service.get_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        output_path = f"exports/order-{order['order_number']}.xlsx"
        os.makedirs('exports', exist_ok=True)
        
        excel_service.export_order_to_excel(order, order.get('items', []), output_path)
        
        return jsonify({
            'success': True,
            'path': output_path
        })
    
    def load_vue_page(page_name):
        """Load Vue.js page template"""
        vue_file = os.path.join(os.path.dirname(__file__), 'js', 'Pages', 'Admin', f'{page_name}.vue')
        
        if not os.path.exists(vue_file):
            return f"<h1>Page not found: {page_name}</h1>"
        
        with open(vue_file, 'r', encoding='utf-8') as f:
            vue_content = f.read()
        
        # Create HTML wrapper with Vue.js and Tailwind
        html_template = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản lý B2B</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body>
    <div id="app">
        <!-- Vue.js content will be rendered here -->
    </div>
    
    <script>
        const {{ createApp }} = Vue;
        
        createApp({{
            data() {{
                return {{
                    orders: [],
                    debts: [],
                    customers: [],
                    stats: {{}},
                    loading: false
                }}
            }},
            mounted() {{
                this.loadData();
            }},
            methods: {{
                async loadData() {{
                    this.loading = true;
                    try {{
                        const response = await axios.get('/api/b2b-orders');
                        this.orders = response.data.data;
                        this.stats = response.data.stats;
                    }} catch (error) {{
                        console.error('Error loading data:', error);
                    }} finally {{
                        this.loading = false;
                    }}
                }}
            }}
        }}).mount('#app');
    </script>
</body>
</html>
        """
        
        return html_template
    
    return app, port
