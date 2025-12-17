from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()

class FinancialData(db.Model):
   
    __tablename__ = 'financial_data'
    
    id = db.Column(db.Integer, primary_key=True)
    
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    revenue = db.Column(db.Numeric(12, 2), nullable=False)
    fixed_costs = db.Column(db.Numeric(12, 2), nullable=False)
    variable_cost_percent = db.Column(db.Numeric(5, 2), nullable=False)
    
    variable_costs = db.Column(db.Numeric(12, 2))
    gross_profit = db.Column(db.Numeric(12, 2))
    net_profit = db.Column(db.Numeric(12, 2))
    profit_margin = db.Column(db.Numeric(5, 2))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_metrics(self):
        
        self.variable_costs = self.revenue * (self.variable_cost_percent / 100)
        
        self.gross_profit = self.revenue - self.variable_costs
   
        self.net_profit = self.gross_profit - self.fixed_costs
        
        if self.revenue > 0:
            self.profit_margin = (self.net_profit / self.revenue) * 100
        else:
            self.profit_margin = 0
    
    def to_dict(self):
       
        return {
            'id': self.id,
            'month': self.month,
            'year': self.year,
            'revenue': float(self.revenue),
            'fixed_costs': float(self.fixed_costs),
            'variable_cost_percent': float(self.variable_cost_percent),
            'variable_costs': float(self.variable_costs) if self.variable_costs else 0,
            'gross_profit': float(self.gross_profit) if self.gross_profit else 0,
            'net_profit': float(self.net_profit) if self.net_profit else 0,
            'profit_margin': float(self.profit_margin) if self.profit_margin else 0,
        }
    
    def __repr__(self):
        return f'<FinancialData {self.month}/{self.year}: Net Profit {self.net_profit}>'


class Forecast(db.Model):
   
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    base_revenue = db.Column(db.Numeric(12, 2), nullable=False)
    growth_rate = db.Column(db.Numeric(5, 2), nullable=False)
    fixed_costs = db.Column(db.Numeric(12, 2), nullable=False)
    variable_cost_percent = db.Column(db.Numeric(5, 2), nullable=False)
    
    months_ahead = db.Column(db.Integer, default=6)
    
    forecast_data = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def generate_forecast(self):
        
        forecast = []
        
        for month in range(1, self.months_ahead + 1):
            
            revenue = float(self.base_revenue) * ((1 + float(self.growth_rate) / 100) ** (month - 1))
            
            variable_costs = revenue * (float(self.variable_cost_percent) / 100)
            
            gross_profit = revenue - variable_costs
            
            net_profit = gross_profit - float(self.fixed_costs)
            
            profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
            
            forecast.append({
                'month': month,
                'revenue': round(revenue, 2),
                'variable_costs': round(variable_costs, 2),
                'gross_profit': round(gross_profit, 2),
                'net_profit': round(net_profit, 2),
                'profit_margin': round(profit_margin, 2)
            })
        
        self.forecast_data = forecast
        return forecast
    
    def __repr__(self):
        return f'<Forecast: {self.months_ahead} months>'
