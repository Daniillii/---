from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, FinancialData, Forecast
from datetime import datetime
import json

def create_app(config_name='development'):
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
 
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app('development')


@app.route('/')
def index():

    all_data = FinancialData.query.order_by(FinancialData.year.desc(), FinancialData.month.desc()).all()
    
    total_revenue = sum(float(d.revenue) for d in all_data) if all_data else 0
    total_profit = sum(float(d.net_profit) if d.net_profit else 0 for d in all_data) if all_data else 0
    avg_margin = (sum(float(d.profit_margin) if d.profit_margin else 0 for d in all_data) / len(all_data)) if all_data else 0
    
    stats = {
        'total_revenue': round(total_revenue, 2),
        'total_profit': round(total_profit, 2),
        'avg_margin': round(avg_margin, 2),
        'data_points': len(all_data)
    }
    
    return render_template('index.html', all_data=all_data, stats=stats)


@app.route('/api/add-data', methods=['POST'])
def add_financial_data():

    try:
        data = request.get_json()
        
        # Валидация
        required_fields = ['month', 'year', 'revenue', 'fixed_costs', 'variable_cost_percent']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Создание записи
        financial_data = FinancialData(
            month=int(data['month']),
            year=int(data['year']),
            revenue=float(data['revenue']),
            fixed_costs=float(data['fixed_costs']),
            variable_cost_percent=float(data['variable_cost_percent'])
        )
        
        # Расчет показателей
        financial_data.calculate_metrics()
        
        db.session.add(financial_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': financial_data.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/forecast', methods=['POST'])
def generate_forecast():
    """API для генерации прогноза"""
    try:
        data = request.get_json()
        
        forecast = Forecast(
            base_revenue=float(data.get('base_revenue', 100000)),
            growth_rate=float(data.get('growth_rate', 5)),
            fixed_costs=float(data.get('fixed_costs', 20000)),
            variable_cost_percent=float(data.get('variable_cost_percent', 40)),
            months_ahead=int(data.get('months_ahead', 12))
        )
        
        forecast_data = forecast.generate_forecast()
        
        db.session.add(forecast)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'forecast': forecast_data,
            'forecast_id': forecast.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/data/<int:data_id>', methods=['GET'])
def get_data(data_id):
    """Получить конкретную запись"""
    data = FinancialData.query.get_or_404(data_id)
    return jsonify(data.to_dict())


@app.route('/api/data/<int:data_id>', methods=['DELETE'])
def delete_data(data_id):
    """Удалить запись"""
    try:
        data = FinancialData.query.get_or_404(data_id)
        db.session.delete(data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Data deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/api/analytics', methods=['GET'])
def get_analytics():

    all_data = FinancialData.query.order_by(FinancialData.year, FinancialData.month).all()
    
    if not all_data:
        return jsonify({'error': 'No data available'}), 404
    
    analytics = {
        'total_revenue': sum(float(d.revenue) for d in all_data),
        'total_costs': sum(float(d.fixed_costs) + float(d.variable_costs if d.variable_costs else 0) for d in all_data),
        'total_profit': sum(float(d.net_profit if d.net_profit else 0) for d in all_data),
        'avg_profit_margin': sum(float(d.profit_margin if d.profit_margin else 0) for d in all_data) / len(all_data),
        'max_profit': max(float(d.net_profit if d.net_profit else 0) for d in all_data),
        'min_profit': min(float(d.net_profit if d.net_profit else 0) for d in all_data),
        'best_month': max(all_data, key=lambda x: x.net_profit if x.net_profit else 0).month if all_data else None,
        'monthly_data': [d.to_dict() for d in all_data]
    }
    
    return jsonify(analytics)


@app.route('/form')
def form():
    
    return render_template('add_data.html')


@app.route('/report')
def report():

    all_data = FinancialData.query.order_by(FinancialData.year, FinancialData.month).all()
    return render_template('report.html', all_data=all_data)


@app.errorhandler(404)
def not_found(error):
    
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(" База данных инициализирована")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
