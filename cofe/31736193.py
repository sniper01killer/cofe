import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from typing import Dict, List, Tuple, Any
import warnings
import json
warnings.filterwarnings('ignore')

# ===================== НАСТРОЙКИ =====================

class CafeConfig:
    N_ROWS = 500
    START_DATE = "2023-10-01"
    
    PRICE_SETTINGS = {
        'coffee':   {'min': 150, 'max': 300, 'cost_%': 30, 'demand_elasticity': -1.2},
        'bakery':   {'min': 80,  'max': 180, 'cost_%': 30, 'demand_elasticity': -1.0},
        'dessert':  {'min': 200, 'max': 400, 'cost_%': 35, 'demand_elasticity': -0.8},
        'sandwich': {'min': 250, 'max': 450, 'cost_%': 40, 'demand_elasticity': -1.5},
        'beverage': {'min': 120, 'max': 220, 'cost_%': 33, 'demand_elasticity': -1.3},
        'tea':      {'min': 100, 'max': 200, 'cost_%': 30, 'demand_elasticity': -1.1},
        'snack':    {'min': 180, 'max': 350, 'cost_%': 38, 'demand_elasticity': -1.4}
    }
    
    PROMO_CHANCE = 30
    WEEKEND_PROMO_BOOST = 20
    
    QUANTITY_DISTRIBUTION = {1: 80, 2: 15, 3: 4, 4: 1}
    KNOWN_CUSTOMER_CHANCE = 70
    LOYALTY_CARD_CHANCE = 60
    
    AGE_GROUP_DISTRIBUTION = {'18-24': 25, '25-34': 40, '35-44': 25, '45-54': 10}
    PEAK_HOURS = {8: 2, 9: 5, 10: 4, 11: 6, 12: 8, 13: 7, 14: 4, 15: 3, 16: 4, 17: 5, 18: 4, 19: 2}
    
    DISH_NAMES = {
        'coffee':   ['Капучино', 'Латте', 'Американо', 'Эспрессо', 'Раф', 'Флэт Уайт', 'Мокко'],
        'bakery':   ['Круассан', 'Маффин', 'Печенье', 'Бейгл', 'Булочка с корицей'],
        'dessert':  ['Тирамису', 'Чизкейк', 'Брауни', 'Макарон', 'Эклер', 'Панна котта', 'Медовик'],
        'sandwich': ['Куриный сэндвич', 'Клаб-сэндвич', 'Вегетарианский сэндвич', 'Сэндвич с лососем'],
        'beverage': ['Лимонад', 'Смузи', 'Айс-кофе', 'Мохито безалкогольный', 'Какао'],
        'tea':      ['Зеленый чай', 'Чай с мятой', 'Черный чай', 'Фруктовый чай'],
        'snack':    ['Салат Цезарь', 'Суп-пюре', 'Кесадилья', 'Салат Греческий']
    }

# ===================== СИСТЕМА СОХРАНЕНИЯ =====================

class DataSaver:
    """Класс для сохранения данных в различные форматы"""
    
    @staticmethod
    def save_dataset(df, filename, format='csv'):
        """Сохранить датасет в указанном формате"""
        try:
            if format.lower() == 'csv':
                # Создаем папку если нет
                os.makedirs('datasets', exist_ok=True)
                filepath = f'datasets/{filename}.csv'
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                return filepath
            
            elif format.lower() == 'excel':
                os.makedirs('datasets', exist_ok=True)
                filepath = f'datasets/{filename}.xlsx'
                df.to_excel(filepath, index=False)
                return filepath
            
            elif format.lower() == 'json':
                os.makedirs('datasets', exist_ok=True)
                filepath = f'datasets/{filename}.json'
                df.to_json(filepath, orient='records', force_ascii=False)
                return filepath
            
            else:
                raise ValueError(f"Неизвестный формат: {format}")
                
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return None
    
    @staticmethod
    def save_forecast(forecast_df, filename):
        """Сохранить прогноз"""
        try:
            os.makedirs('forecasts', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filepath = f'forecasts/{filename}_{timestamp}.csv'
            forecast_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return filepath
        except Exception as e:
            print(f"❌ Ошибка при сохранении прогноза: {e}")
            return None
    
    @staticmethod
    def save_changes_history(changes, filename):
        """Сохранить историю изменений"""
        try:
            os.makedirs('history', exist_ok=True)
            filepath = f'history/{filename}.json'
            
            # Конвертируем datetime в строки для JSON
            serializable_changes = []
            for change in changes:
                serializable_change = change.copy()
                if 'timestamp' in serializable_change:
                    serializable_change['timestamp'] = serializable_change['timestamp'].isoformat()
                serializable_changes.append(serializable_change)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_changes, f, ensure_ascii=False, indent=2)
            
            return filepath
        except Exception as e:
            print(f"❌ Ошибка при сохранении истории: {e}")
            return None
    
    @staticmethod
    def save_config(config, filename):
        """Сохранить конфигурацию"""
        try:
            os.makedirs('configs', exist_ok=True)
            filepath = f'configs/{filename}.json'
            
            # Создаем сериализуемый словарь конфигурации
            config_dict = {
                'PRICE_SETTINGS': config.PRICE_SETTINGS,
                'PROMO_CHANCE': config.PROMO_CHANCE,
                'KNOWN_CUSTOMER_CHANCE': config.KNOWN_CUSTOMER_CHANCE,
                'LOYALTY_CARD_CHANCE': config.LOYALTY_CARD_CHANCE,
                'AGE_GROUP_DISTRIBUTION': config.AGE_GROUP_DISTRIBUTION,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            
            return filepath
        except Exception as e:
            print(f"❌ Ошибка при сохранении конфигурации: {e}")
            return None
    
    @staticmethod
    def save_analysis_report(report_text, filename):
        """Сохранить отчет анализа"""
        try:
            os.makedirs('reports', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filepath = f'reports/{filename}_{timestamp}.txt'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            return filepath
        except Exception as e:
            print(f"❌ Ошибка при сохранении отчета: {e}")
            return None

# ===================== МОДЕЛЬ ПРОГНОЗИРОВАНИЯ =====================

class DemandForecastModel:
    """Простая модель прогнозирования спроса и прибыли"""
    
    def __init__(self, historical_data):
        self.historical_data = historical_data
        self._train_models()
    
    def _train_models(self):
        """Обучение простых моделей прогнозирования"""
        df = self.historical_data.copy()
        
        if isinstance(df['timestamp'].iloc[0], str):
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
        else:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Прогноз по категориям
        daily_category = df.groupby(['date', 'dish_category']).agg({
            'quantity': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        self.category_means = daily_category.groupby('dish_category').agg({
            'quantity': 'mean',
            'profit': 'mean'
        }).to_dict()
        
        # Прогноз по часам
        if 'hour' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour if isinstance(df['timestamp'].iloc[0], str) else df['timestamp'].dt.hour
            hourly_stats = df.groupby('hour').agg({
                'quantity': 'mean',
                'profit': 'mean'
            }).to_dict()
            self.hourly_means = hourly_stats
        
        # Сезонность по дням недели
        df['weekday'] = pd.to_datetime(df['timestamp']).dt.weekday
        weekday_stats = df.groupby('weekday').agg({
            'quantity': 'mean',
            'profit': 'mean'
        }).to_dict()
        self.weekday_means = weekday_stats
        
    def forecast_demand(self, days=7, changes=None):
        """Прогноз спроса на N дней вперед с учетом изменений"""
        changes = changes or {}
        
        base_daily_profit = self.historical_data['profit'].mean() * 50 if len(self.historical_data) > 0 else 10000
        adjusted_profit = base_daily_profit
        
        if 'price_changes' in changes:
            for category, change_pct in changes['price_changes'].items():
                if category in self.category_means.get('profit', {}):
                    elasticity = CafeConfig.PRICE_SETTINGS[category]['demand_elasticity']
                    quantity_change = elasticity * (change_pct / 100)
                    profit_change = (1 + change_pct/100) * (1 + quantity_change) - 1
                    adjusted_profit *= (1 + profit_change * 0.3)
        
        if 'promo_increase' in changes:
            promo_effect = min(changes['promo_increase'] * 0.15, 0.5)
            adjusted_profit *= (1 + promo_effect)
        
        if 'new_customers_pct' in changes:
            customer_effect = changes['new_customers_pct'] * 0.8 / 100
            adjusted_profit *= (1 + customer_effect)
        
        forecast_dates = [datetime.now().date() + timedelta(days=i) for i in range(days)]
        forecast_data = []
        
        for i, date in enumerate(forecast_dates):
            weekday = date.weekday()
            weekday_profit_mean = self.weekday_means.get('profit', {}).get(weekday)
            weekday_factor = weekday_profit_mean / base_daily_profit if weekday_profit_mean and base_daily_profit > 0 else 1.0
            
            random_factor = 1 + random.uniform(-0.15, 0.15)
            daily_profit = adjusted_profit * weekday_factor * random_factor
            
            forecast_data.append({
                'date': date,
                'day': i+1,
                'weekday': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][weekday],
                'predicted_profit': daily_profit,
                'predicted_customers': int(daily_profit / (self.historical_data['profit'].mean() if len(self.historical_data) > 0 else 200)),
                'predicted_revenue': daily_profit / 0.3  # Предполагаем 30% маржу
            })
        
        return pd.DataFrame(forecast_data)

# ===================== СИМУЛЯТОР РЕАЛЬНОГО ВРЕМЕНИ =====================

class RealTimeCafeSimulator:
    """Симулятор кафе для тестирования рекомендаций в реальном времени"""
    
    def __init__(self, historical_data, config):
        self.historical_data = historical_data
        self.config = config
        self.current_state = self._get_current_state()
        self.applied_changes = []
        self.forecast_model = DemandForecastModel(historical_data)
        self.data_saver = DataSaver()
        
        # Автоматически сохраняем начальный датасет
        self._auto_save_initial_data()
    
    def _auto_save_initial_data(self):
        """Автоматическое сохранение начальных данных"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"initial_dataset_{timestamp}"
        
        # Сохраняем датасет
        saved_file = self.data_saver.save_dataset(
            self.historical_data, 
            filename, 
            format='csv'
        )
        
        if saved_file:
            print(f"💾 Начальный датасет сохранен: {saved_file}")
        
        # Сохраняем конфигурацию
        config_file = self.data_saver.save_config(self.config, f"config_{timestamp}")
        if config_file:
            print(f"⚙️ Конфигурация сохранена: {config_file}")
    
    def _get_current_state(self):
        """Текущее состояние кафе"""
        df = self.historical_data
        
        state = {
            'avg_daily_profit': 0,
            'avg_ticket': 0,
            'customer_count': 0,
            'conversion_rate': 0,
            'top_category': 'N/A',
            'promo_rate': 0,
            'avg_rating': 0,
            'total_transactions': len(df),
            'total_profit': df['profit'].sum() if len(df) > 0 else 0
        }
        
        if len(df) > 0:
            if 'timestamp' in df.columns:
                try:
                    if isinstance(df['timestamp'].iloc[0], str):
                        df['date'] = pd.to_datetime(df['timestamp']).dt.date
                    else:
                        df['date'] = pd.to_datetime(df['timestamp']).dt.date
                    
                    daily_profits = df.groupby('date')['profit'].sum()
                    state['avg_daily_profit'] = daily_profits.mean() if len(daily_profits) > 0 else 0
                except:
                    state['avg_daily_profit'] = df['profit'].mean() * 3
            
            if 'price' in df.columns:
                state['avg_ticket'] = df['price'].mean()
            
            if 'client_id' in df.columns:
                valid_clients = df['client_id'].dropna()
                state['customer_count'] = valid_clients.nunique()
                state['conversion_rate'] = len(valid_clients) / len(df) if len(df) > 0 else 0
            else:
                state['customer_count'] = int(len(df) * 0.7)
                state['conversion_rate'] = 0.7
            
            if 'dish_category' in df.columns and not df['dish_category'].empty:
                state['top_category'] = df['dish_category'].mode().iloc[0] if len(df['dish_category'].mode()) > 0 else 'N/A'
            
            if 'promo_applied' in df.columns:
                state['promo_rate'] = df['promo_applied'].mean()
            
            if 'rating' in df.columns and df['rating'].notna().any():
                state['avg_rating'] = df['rating'].mean()
        
        return state
    
    def apply_recommendation(self, rec_type, params):
        """Применить рекомендацию и рассчитать эффект"""
        
        effects = {
            'profit_impact': 0,
            'customer_impact': 0,
            'description': ''
        }
        
        if rec_type == 'price_change':
            category = params.get('category', 'coffee')
            change_pct = params.get('change_pct', 0)
            
            if category in self.config.PRICE_SETTINGS:
                old_min = self.config.PRICE_SETTINGS[category]['min']
                old_max = self.config.PRICE_SETTINGS[category]['max']
                
                self.config.PRICE_SETTINGS[category]['min'] = int(old_min * (1 + change_pct/100))
                self.config.PRICE_SETTINGS[category]['max'] = int(old_max * (1 + change_pct/100))
                
                elasticity = self.config.PRICE_SETTINGS[category]['demand_elasticity']
                
                if change_pct > 0:
                    effects['profit_impact'] = 0.08 * change_pct
                    effects['customer_impact'] = -0.05 * abs(change_pct)
                    effects['description'] = f"Цены на {category} изменены на {change_pct:+}%"
                else:
                    effects['profit_impact'] = -0.03 * abs(change_pct)
                    effects['customer_impact'] = 0.08 * abs(change_pct)
                    effects['description'] = f"Скидка на {category} {abs(change_pct)}%"
            else:
                effects['description'] = f"Категория {category} не найдена"
        
        elif rec_type == 'promo_campaign':
            duration = params.get('duration', 7)
            discount = params.get('discount', 15)
            
            self.config.PROMO_CHANCE = min(100, self.config.PROMO_CHANCE + 30)
            
            effects['profit_impact'] = -0.1
            effects['customer_impact'] = 0.25
            effects['description'] = f"Акция: скидка {discount}% на {duration} дней"
        
        elif rec_type == 'happy_hours':
            hours = params.get('hours', '15-17')
            discount = params.get('discount', 20)
            
            effects['profit_impact'] = 0.15
            effects['customer_impact'] = 0.20
            effects['description'] = f"Счастливые часы {hours} со скидкой {discount}%"
        
        elif rec_type == 'menu_change':
            action = params.get('action', 'add')
            dish = params.get('dish', '')
            
            if action == 'add':
                effects['profit_impact'] = 0.05
                effects['customer_impact'] = 0.03
                effects['description'] = f"Добавлено новое блюдо: {dish}"
            elif action == 'remove':
                effects['profit_impact'] = 0.02
                effects['customer_impact'] = -0.01
                effects['description'] = f"Удалено блюдо: {dish}"
        
        elif rec_type == 'loyalty_program':
            improvement = params.get('improvement', '')
            
            self.config.LOYALTY_CARD_CHANCE = min(100, self.config.LOYALTY_CARD_CHANCE + 20)
            
            effects['profit_impact'] = 0.12
            effects['customer_impact'] = 0.15
            effects['description'] = f"Улучшена программа лояльности: {improvement}"
        
        # Сохраняем изменение
        change_record = {
            'timestamp': datetime.now(),
            'type': rec_type,
            'params': params,
            'effects': effects.copy()
        }
        self.applied_changes.append(change_record)
        
        # Автоматически сохраняем после каждого изменения
        self._auto_save_after_change(change_record)
        
        return effects
    
    def _auto_save_after_change(self, change_record):
        """Автоматическое сохранение после применения рекомендации"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # 1. Сохраняем историю изменений
        history_file = self.data_saver.save_changes_history(
            self.applied_changes, 
            f"changes_history_{timestamp}"
        )
        
        # 2. Сохраняем обновленную конфигурацию
        config_file = self.data_saver.save_config(
            self.config, 
            f"config_after_change_{timestamp}"
        )
        
        # 3. Сохраняем симулированные данные после изменения
        self._generate_and_save_updated_data(timestamp)
        
        print(f"💾 Данные сохранены после применения: {change_record['effects']['description']}")
    
    def _generate_and_save_updated_data(self, timestamp):
        """Генерируем и сохраняем обновленные данные после изменений"""
        # Генерируем новые данные с обновленной конфигурацией
        new_data = self._generate_simulated_data(days=30)
        
        if new_data is not None and len(new_data) > 0:
            # Сохраняем новые данные
            filename = f"simulated_data_after_changes_{timestamp}"
            saved_file = self.data_saver.save_dataset(new_data, filename, format='csv')
            
            if saved_file:
                print(f"📊 Сгенерирован новый датасет: {saved_file}")
    
    def _generate_simulated_data(self, days=30):
        """Генерируем симулированные данные на основе текущей конфигурации"""
        try:
            np.random.seed(42)
            random.seed(42)
            
            data = []
            start_date = datetime.now()
            
            for i in range(days * 50):  # Примерно 50 транзакций в день
                current_date = start_date + timedelta(days=i//50)
                hour = random.choices(list(self.config.PEAK_HOURS.keys()), 
                                     weights=list(self.config.PEAK_HOURS.values()))[0]
                timestamp = current_date.replace(hour=hour, minute=random.randint(0, 59))
                
                category = random.choice(list(self.config.PRICE_SETTINGS.keys()))
                price_settings = self.config.PRICE_SETTINGS[category]
                price = random.randint(price_settings['min'], price_settings['max'])
                cost = price * price_settings['cost_%'] / 100
                quantity = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
                profit = (price - cost) * quantity
                
                # Клиент
                if random.random() < self.config.KNOWN_CUSTOMER_CHANCE / 100:
                    client_id = f'C-{random.randint(1000, 9999)}'
                else:
                    client_id = None
                
                data.append({
                    'timestamp': timestamp,
                    'transaction_id': f'T{10000 + i}',
                    'client_id': client_id,
                    'dish_category': category,
                    'dish_name': random.choice(self.config.DISH_NAMES.get(category, ['Неизвестно'])),
                    'price': price,
                    'cost': cost,
                    'quantity': quantity,
                    'profit': profit,
                    'promo_applied': 1 if random.random() < self.config.PROMO_CHANCE/100 else 0,
                    'predicted_profit_margin': (price - cost) / price if price > 0 else 0
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"❌ Ошибка генерации данных: {e}")
            return None
    
    def get_forecast(self, days=30, scenario=None):
        """Получить прогноз на N дней с учетом примененных изменений"""
        
        changes_summary = {}
        for change in self.applied_changes[-5:]:
            if change['type'] == 'price_change':
                if 'price_changes' not in changes_summary:
                    changes_summary['price_changes'] = {}
                cat = change['params'].get('category', 'coffee')
                pct = change['params'].get('change_pct', 0)
                changes_summary['price_changes'][cat] = changes_summary['price_changes'].get(cat, 0) + pct
        
        if scenario == 'optimistic':
            changes_summary['new_customers_pct'] = 20
            changes_summary['promo_increase'] = 10
        elif scenario == 'pessimistic':
            changes_summary['new_customers_pct'] = -10
            changes_summary['promo_increase'] = -5
        
        forecast = self.forecast_model.forecast_demand(days, changes_summary)
        
        if len(forecast) > 0:
            forecast['cumulative_profit'] = forecast['predicted_profit'].cumsum()
        
        return forecast
    
    def save_current_state(self, prefix="cafe_state"):
        """Сохранить текущее состояние системы"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # 1. Сохраняем исторические данные
        hist_file = self.data_saver.save_dataset(
            self.historical_data, 
            f"{prefix}_historical_{timestamp}", 
            format='csv'
        )
        
        # 2. Сохраняем прогноз на 30 дней
        forecast = self.get_forecast(30)
        if len(forecast) > 0:
            forecast_file = self.data_saver.save_forecast(
                forecast, 
                f"{prefix}_forecast_{timestamp}"
            )
        
        # 3. Сохраняем конфигурацию
        config_file = self.data_saver.save_config(
            self.config, 
            f"{prefix}_config_{timestamp}"
        )
        
        # 4. Сохраняем историю изменений
        history_file = self.data_saver.save_changes_history(
            self.applied_changes, 
            f"{prefix}_changes_{timestamp}"
        )
        
        # 5. Сохраняем текущее состояние
        state_df = pd.DataFrame([self.current_state])
        state_file = self.data_saver.save_dataset(
            state_df, 
            f"{prefix}_current_state_{timestamp}", 
            format='csv'
        )
        
        print(f"\n💾 Текущее состояние сохранено:")
        print(f"   • Исторические данные: {hist_file}")
        if 'forecast_file' in locals():
            print(f"   • Прогноз: {forecast_file}")
        print(f"   • Конфигурация: {config_file}")
        print(f"   • История изменений: {history_file}")
        print(f"   • Текущее состояние: {state_file}")
        
        return {
            'historical': hist_file,
            'forecast': forecast_file if 'forecast_file' in locals() else None,
            'config': config_file,
            'changes': history_file,
            'state': state_file
        }
    
    def compare_scenarios(self):
        """Сравнение разных сценариев развития"""
        
        scenarios = {
            'Базовый': {},
            'Активное продвижение': {'promo_increase': 30, 'new_customers_pct': 15},
            'Повышение цен': {'price_changes': {'coffee': 10, 'dessert': 10}},
            'Оптимизация меню': {'new_customers_pct': 5}
        }
        
        comparison = []
        base_forecast = None
        
        for name, changes in scenarios.items():
            forecast = self.forecast_model.forecast_demand(30, changes)
            total_profit = forecast['predicted_profit'].sum() if len(forecast) > 0 else 0
            avg_daily = forecast['predicted_profit'].mean() if len(forecast) > 0 else 0
            
            if name == 'Базовый':
                base_forecast = total_profit
            
            growth = 0
            if base_forecast and base_forecast > 0:
                growth = ((total_profit / base_forecast) - 1) * 100
            
            comparison.append({
                'Сценарий': name,
                'Общая прибыль (30 дней)': f"{total_profit:,.0f} руб.",
                'Среднедневная': f"{avg_daily:,.0f} руб.",
                'Рост к базовому': f"{growth:+.1f}%"
            })
        
        return pd.DataFrame(comparison)
    
    def generate_roi_analysis(self, investment, change_type):
        """Анализ окупаемости инвестиций"""
        
        forecast = self.get_forecast(90)
        
        if len(forecast) == 0:
            return {
                'investment': investment,
                'additional_profit_expected': 0,
                'roi_percent': -100,
                'payback_months': float('inf'),
                'recommendation': 'НЕДОСТАТОЧНО ДАННЫХ'
            }
        
        monthly_profit = forecast['predicted_profit'].sum() / 3
        
        if change_type == 'marketing':
            effect_multiplier = 1.5
            duration_months = 3
        elif change_type == 'equipment':
            effect_multiplier = 1.2
            duration_months = 12
        elif change_type == 'training':
            effect_multiplier = 1.15
            duration_months = 6
        else:
            effect_multiplier = 1.1
            duration_months = 6
        
        improved_monthly = monthly_profit * effect_multiplier
        additional_profit = (improved_monthly - monthly_profit) * duration_months
        
        roi = (additional_profit - investment) / investment * 100 if investment > 0 else 0
        payback_months = investment / (improved_monthly - monthly_profit) if improved_monthly > monthly_profit else float('inf')
        
        recommendation = 'РЕКОМЕНДУЕМ' if roi > 30 else 'НЕ РЕКОМЕНДУЕМ' if roi < 0 else 'РАССМОТРЕТЬ'
        
        return {
            'investment': investment,
            'additional_profit_expected': additional_profit,
            'roi_percent': roi,
            'payback_months': payback_months,
            'recommendation': recommendation
        }

# ===================== ИНТЕРАКТИВНЫЙ ИНТЕРФЕЙС =====================

class RealTimeCafeDashboard:
    """Интерактивная панель управления кафе в реальном времени"""
    
    def __init__(self):
        self.config = CafeConfig()
        self.historical_data = self._generate_initial_data()
        self.simulator = RealTimeCafeSimulator(self.historical_data, self.config)
        self.running = True
    
    def _generate_initial_data(self):
        """Генерация начальных исторических данных с ВСЕМИ необходимыми столбцами"""
        np.random.seed(42)
        random.seed(42)
        
        data = []
        start_date = datetime.strptime(self.config.START_DATE, "%Y-%m-%d")
        
        for i in range(self.config.N_ROWS):
            day_offset = random.randint(0, 60)
            current_date = start_date + timedelta(days=day_offset)
            hour = random.choices(list(self.config.PEAK_HOURS.keys()), 
                                 weights=list(self.config.PEAK_HOURS.values()))[0]
            timestamp = current_date.replace(hour=hour, minute=random.randint(0, 59))
            
            # Выбираем категорию
            category = random.choice(list(self.config.PRICE_SETTINGS.keys()))
            
            # Выбираем конкретное блюдо
            dish_name = random.choice(self.config.DISH_NAMES.get(category, ['Неизвестно']))
            
            # Генерация цены и стоимости
            price_settings = self.config.PRICE_SETTINGS[category]
            price = random.randint(price_settings['min'], price_settings['max'])
            cost = price * price_settings['cost_%'] / 100
            
            # Количество
            quantity = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
            
            # Прибыль
            profit = (price - cost) * quantity
            
            # Акция
            promo_applied = 1 if random.random() < self.config.PROMO_CHANCE/100 else 0
            
            # Клиент (может быть None)
            if random.random() < self.config.KNOWN_CUSTOMER_CHANCE / 100:
                client_id = f'C-{random.randint(100, 999)}'
                
                # Возрастная группа
                age_groups = list(self.config.AGE_GROUP_DISTRIBUTION.keys())
                age_weights = list(self.config.AGE_GROUP_DISTRIBUTION.values())
                age_group = random.choices(age_groups, weights=age_weights)[0]
                
                # Лояльность
                is_loyalty = 1 if random.random() < self.config.LOYALTY_CARD_CHANCE / 100 else 0
            else:
                client_id = None
                age_group = None
                is_loyalty = 0
            
            # Рейтинг
            if random.random() < 0.7:
                rating = random.choices([4, 5, 3], weights=[50, 30, 20])[0]
            else:
                rating = None
            
            # День недели
            weekday = timestamp.weekday()
            week_day = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][weekday]
            is_weekend = 1 if weekday >= 5 else 0
            
            # ID официанта и время приготовления
            waiter_id = f'W-{random.randint(1, 10):02d}'
            
            # Время приготовления в зависимости от категории
            prep_times = {
                'coffee': (2, 5), 'bakery': (1, 3), 'dessert': (3, 6),
                'sandwich': (5, 10), 'beverage': (2, 4), 'tea': (1, 3),
                'snack': (4, 8)
            }
            prep_min, prep_max = prep_times.get(category, (2, 5))
            preparation_time = random.randint(prep_min, prep_max)
            
            # Маржа прибыли
            profit_margin = (price - cost) / price if price > 0 else 0
            
            data.append({
                'transaction_id': f'T{1000+i}',
                'timestamp': timestamp,
                'client_id': client_id,
                'age_group': age_group,
                'is_loyalty': is_loyalty,
                'week_day': week_day,
                'hour': hour,
                'is_weekend': is_weekend,
                'is_holiday': 0,
                'dish_id': f'D-{random.randint(100, 500)}',
                'dish_name': dish_name,
                'dish_category': category,
                'price': price,
                'cost': cost,
                'quantity': quantity,
                'weather': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Clear']),
                'temperature': random.randint(15, 25),
                'promo_applied': promo_applied,
                'waiter_id': waiter_id,
                'preparation_time': preparation_time,
                'rating': rating,
                'predicted_profit_margin': round(profit_margin, 3),
                'profit': profit
            })
        
        return pd.DataFrame(data)
    
    def display_dashboard(self):
        """Отображение основной панели"""
        print("\n" + "="*70)
        print("🏪 ПАНЕЛЬ УПРАВЛЕНИЯ КАФЕ В РЕАЛЬНОМ ВРЕМЕНИ")
        print("="*70)
        
        state = self.simulator.current_state
        
        print(f"\n📊 ТЕКУЩИЕ ПОКАЗАТЕЛИ:")
        print(f"  • Средняя дневная прибыль: {state['avg_daily_profit']:,.0f} руб.")
        print(f"  • Средний чек: {state['avg_ticket']:.0f} руб.")
        print(f"  • Постоянных клиентов: {state['customer_count']}")
        print(f"  • Доля акционных продаж: {state['promo_rate']:.1%}")
        print(f"  • Рейтинг: {state['avg_rating']:.1f}/5")
        print(f"  • Популярная категория: {state['top_category']}")
        print(f"  • Всего транзакций: {state['total_transactions']}")
        print(f"  • Общая прибыль: {state['total_profit']:,.0f} руб.")
        
        if self.simulator.applied_changes:
            print(f"\n🔄 ПРИМЕНЕННЫЕ ИЗМЕНЕНИЯ:")
            for i, change in enumerate(self.simulator.applied_changes[-3:], 1):
                desc = change['effects'].get('description', 'Без описания')
                print(f"  {i}. {desc}")
    
    def show_recommendations(self):
        """Показать доступные рекомендации"""
        print("\n🎯 ДОСТУПНЫЕ РЕКОМЕНДАЦИИ:")
        print("1. 📈 Изменить цены на категорию")
        print("2. 🎪 Запустить промо-кампанию")
        print("3. ⏰ Ввести счастливые часы")
        print("4. 📝 Изменить меню")
        print("5. 👑 Улучшить программу лояльности")
        print("6. 📊 Показать прогнозы")
        print("7. 🔄 Сравнить сценарии")
        print("8. 💰 Анализ окупаемости инвестиций")
        print("9. 📈 Показать исторические данные")
        print("10. 💾 Сохранить все данные (датасет + состояние)")
        print("11. 📁 Экспорт данных для ML")
        print("0. ⏹️ Выйти")
    
    def apply_price_change(self):
        """Интерфейс изменения цен"""
        print("\n📈 ИЗМЕНЕНИЕ ЦЕН")
        print("Доступные категории:", ", ".join(self.config.PRICE_SETTINGS.keys()))
        
        category = input("Категория: ").strip().lower()
        if category not in self.config.PRICE_SETTINGS:
            print("❌ Ошибка: категория не найдена")
            return
        
        try:
            change = float(input("Изменение (%): "))
        except:
            print("❌ Ошибка: введите число")
            return
        
        params = {'category': category, 'change_pct': change}
        effects = self.simulator.apply_recommendation('price_change', params)
        
        print(f"\n✅ Применено: {effects['description']}")
        print(f"📊 Ожидаемый эффект:")
        print(f"  • Влияние на прибыль: {effects['profit_impact']:+.1%}")
        print(f"  • Влияние на клиентов: {effects['customer_impact']:+.1%}")
        
        # Автоматически сохраняем после применения
        self._auto_save_after_action("price_change")
    
    def apply_promo_campaign(self):
        """Интерфейс запуска промо-кампании"""
        print("\n🎪 ЗАПУСК ПРОМО-КАМПАНИИ")
        
        try:
            discount = float(input("Скидка (%): "))
            duration = int(input("Длительность (дни): "))
        except:
            print("❌ Ошибка: введите числа")
            return
        
        params = {'discount': discount, 'duration': duration}
        effects = self.simulator.apply_recommendation('promo_campaign', params)
        
        print(f"\n✅ Применено: {effects['description']}")
        print(f"📊 Ожидаемый эффект:")
        print(f"  • Влияние на прибыль: {effects['profit_impact']:+.1%}")
        print(f"  • Влияние на клиентов: {effects['customer_impact']:+.1%}")
        
        self._auto_save_after_action("promo_campaign")
    
    def _auto_save_after_action(self, action_type):
        """Автоматическое сохранение после действия"""
        save = input("\n💾 Автоматически сохранить датасет? (да/нет): ").strip().lower()
        if save in ['да', 'д', 'yes', 'y', '1']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"dataset_after_{action_type}_{timestamp}"
            
            # Сохраняем в нескольких форматах
            saved_files = []
            
            # CSV
            csv_file = DataSaver.save_dataset(self.historical_data, filename, 'csv')
            if csv_file:
                saved_files.append(f"CSV: {csv_file}")
            
            # Excel
            excel_file = DataSaver.save_dataset(self.historical_data, filename, 'excel')
            if excel_file:
                saved_files.append(f"Excel: {excel_file}")
            
            if saved_files:
                print("✅ Датасет сохранен в файлах:")
                for file in saved_files:
                    print(f"   • {file}")
    
    def show_forecasts(self):
        """Показать прогнозы"""
        print("\n📊 ПРОГНОЗЫ НА БУДУЩИЕ ПЕРИОДЫ")
        
        print("\n1. Прогноз на 7 дней")
        print("2. Прогноз на 30 дней")
        print("3. Прогноз на 90 дней")
        print("4. Прогноз с оптимистичным сценарием")
        print("5. Прогноз с пессимистичным сценарием")
        
        choice = input("Выберите период: ").strip()
        
        if choice == '1':
            days = 7
            scenario = None
        elif choice == '2':
            days = 30
            scenario = None
        elif choice == '3':
            days = 90
            scenario = None
        elif choice == '4':
            days = 30
            scenario = 'optimistic'
        elif choice == '5':
            days = 30
            scenario = 'pessimistic'
        else:
            days = 30
            scenario = None
        
        forecast = self.simulator.get_forecast(days, scenario)
        
        if len(forecast) == 0:
            print("❌ Не удалось сгенерировать прогноз. Недостаточно данных.")
            return
        
        print(f"\n📅 Прогноз на {days} дней ({'оптимистичный' if scenario == 'optimistic' else 'пессимистичный' if scenario == 'pessimistic' else 'базовый'} сценарий):")
        print("-" * 60)
        print(f"{'День':<5} {'Дата':<12} {'День недели':<12} {'Прибыль':<12} {'Кумулятивная':<15}")
        print("-" * 60)
        
        for _, row in forecast.iterrows():
            print(f"{row['day']:<5} {row['date']:<12} {row['weekday']:<12} {row['predicted_profit']:<12.0f} {row['cumulative_profit']:<15.0f}")
        
        total_profit = forecast['predicted_profit'].sum()
        print("-" * 60)
        print(f"Итого прибыль за {days} дней: {total_profit:,.0f} руб.")
        
        # Предлагаем сохранить прогноз
        save_forecast = input("\n💾 Сохранить прогноз в файл? (да/нет): ").strip().lower()
        if save_forecast in ['да', 'д', 'yes', 'y', '1']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"forecast_{days}days_{scenario if scenario else 'base'}_{timestamp}"
            saved_file = DataSaver.save_forecast(forecast, filename)
            if saved_file:
                print(f"✅ Прогноз сохранен: {saved_file}")
    
    def save_all_data(self):
        """Сохранить все данные системы"""
        print("\n💾 СОХРАНЕНИЕ ВСЕХ ДАННЫХ")
        print("="*50)
        
        prefix = input("Введите префикс для имен файлов (или нажмите Enter для стандартного): ").strip()
        if not prefix:
            prefix = "cafe_data"
        
        # Сохраняем текущее состояние
        saved_files = self.simulator.save_current_state(prefix)
        
        # Дополнительно сохраняем полный датасет
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        full_dataset_file = DataSaver.save_dataset(
            self.historical_data, 
            f"{prefix}_full_dataset_{timestamp}", 
            'csv'
        )
        
        print(f"\n📦 Полный датасет сохранен: {full_dataset_file}")
        
        # Создаем README файл с описанием
        self._create_readme_file(prefix, timestamp, saved_files, full_dataset_file)
    
    def _create_readme_file(self, prefix, timestamp, saved_files, dataset_file):
        """Создать README файл с описанием данных"""
        readme_content = f"""# Датсет кафе для ML проекта

## Основная информация
- Дата генерации: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Префикс файлов: {prefix}
- Количество транзакций: {len(self.historical_data)}
- Период данных: {self.historical_data['timestamp'].min()} - {self.historical_data['timestamp'].max()}

## Файлы данных:
1. Исторические данные: {saved_files.get('historical', 'N/A')}
2. Прогноз: {saved_files.get('forecast', 'N/A')}
3. Конфигурация: {saved_files.get('config', 'N/A')}
4. История изменений: {saved_files.get('changes', 'N/A')}
5. Текущее состояние: {saved_files.get('state', 'N/A')}
6. Полный датасет: {dataset_file}

## Структура датасета:
- transaction_id: ID транзакции
- timestamp: Дата и время
- client_id: ID клиента (может быть None)
- dish_category: Категория блюда
- dish_name: Название блюда
- price: Цена продажи
- cost: Себестоимость
- quantity: Количество
- profit: Прибыль
- promo_applied: Применена ли акция (0/1)
- rating: Оценка клиента

## Примененные изменения:
"""
        
        if self.simulator.applied_changes:
            for i, change in enumerate(self.simulator.applied_changes, 1):
                readme_content += f"{i}. {change['effects'].get('description', 'Без описания')}\n"
        
        readme_content += f"\n## Ключевые метрики:\n"
        state = self.simulator.current_state
        for key, value in state.items():
            readme_content += f"- {key}: {value}\n"
        
        # Сохраняем README
        readme_file = DataSaver.save_analysis_report(
            readme_content,
            f"{prefix}_README_{timestamp}"
        )
        
        if readme_file:
            print(f"📄 README файл создан: {readme_file}")
    
    def export_for_ml(self):
        """Экспорт данных для машинного обучения"""
        print("\n🤖 ЭКСПОРТ ДАННЫХ ДЛЯ МАШИННОГО ОБУЧЕНИЯ")
        print("="*50)
        
        print("\nДоступные форматы экспорта:")
        print("1. CSV для классических ML моделей")
        print("2. JSON для глубокого обучения")
        print("3. Excel для анализа")
        print("4. Все форматы")
        
        choice = input("\nВыберите формат (1-4): ").strip()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        prefix = f"ml_dataset_{timestamp}"
        
        # Подготавливаем данные для ML
        ml_data = self._prepare_ml_data()
        
        saved_files = []
        
        if choice in ['1', '4']:
            csv_file = DataSaver.save_dataset(ml_data, f"{prefix}_ml", 'csv')
            if csv_file:
                saved_files.append(f"CSV: {csv_file}")
        
        if choice in ['2', '4']:
            json_file = DataSaver.save_dataset(ml_data, f"{prefix}_ml", 'json')
            if json_file:
                saved_files.append(f"JSON: {json_file}")
        
        if choice in ['3', '4']:
            excel_file = DataSaver.save_dataset(ml_data, f"{prefix}_ml", 'excel')
            if excel_file:
                saved_files.append(f"Excel: {excel_file}")
        
        if saved_files:
            print("\n✅ Данные для ML экспортированы:")
            for file in saved_files:
                print(f"   • {file}")
            
            # Сохраняем описание признаков
            self._save_feature_description(ml_data, prefix)
    
    def _prepare_ml_data(self):
        """Подготовить данные для машинного обучения"""
        df = self.historical_data.copy()
        
        # Создаем дополнительные признаки для ML
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.weekday
            df['month'] = df['timestamp'].dt.month
            df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        
        # One-hot encoding для категориальных признаков
        if 'dish_category' in df.columns:
            category_dummies = pd.get_dummies(df['dish_category'], prefix='category')
            df = pd.concat([df, category_dummies], axis=1)
        
        # Создаем целевую переменную для бинарной классификации
        df['high_profit'] = df['profit'].apply(lambda x: 1 if x > df['profit'].median() else 0)
        
        # Создаем признак для регрессии
        df['profit_margin'] = (df['price'] - df['cost']) / df['price']
        
        # Отбираем наиболее важные признаки для ML
        ml_features = [
            'price', 'cost', 'quantity', 'hour', 'day_of_week', 
            'month', 'is_weekend', 'promo_applied', 'rating',
            'high_profit', 'profit_margin', 'profit'
        ]
        
        # Добавляем one-hot encoded категории
        category_cols = [col for col in df.columns if col.startswith('category_')]
        ml_features.extend(category_cols)
        
        # Выбираем только существующие колонки
        existing_features = [col for col in ml_features if col in df.columns]
        
        return df[existing_features]
    
    def _save_feature_description(self, ml_data, prefix):
        """Сохранить описание признаков для ML"""
        feature_desc = """# Описание признаков для ML модели

## Целевые переменные:
1. profit - Прибыль (регрессия)
2. high_profit - Высокая прибыль (1 если прибыль выше медианы, 0 иначе) (классификация)
3. profit_margin - Маржа прибыли (регрессия)

## Признаки:
1. price - Цена товара
2. cost - Себестоимость
3. quantity - Количество
4. hour - Час дня (0-23)
5. day_of_week - День недели (0-6, где 0 - понедельник)
6. month - Месяц (1-12)
7. is_weekend - Выходной день (1 если суббота/воскресенье, 0 иначе)
8. promo_applied - Применена акция (0/1)
9. rating - Оценка клиента (1-5)

## One-hot encoded категории блюд:
- category_coffee - Кофе
- category_bakery - Выпечка
- category_dessert - Десерты
- category_sandwich - Сэндвичи
- category_beverage - Напитки
- category_tea - Чай
- category_snack - Закуски

## Примеры задач ML:
1. Прогнозирование прибыли (регрессия)
2. Классификация высокоприбыльных транзакций
3. Прогнозирование спроса по категориям
4. Рекомендательные системы
5. Анализ эффективности акций

## Размер датасета:
"""
        feature_desc += f"- Строк: {len(ml_data)}\n"
        feature_desc += f"- Столбцов: {len(ml_data.columns)}\n"
        feature_desc += f"- Признаков для обучения: {len(ml_data.columns) - 3} (исключая целевые переменные)\n"
        
        # Сохраняем описание
        desc_file = DataSaver.save_analysis_report(
            feature_desc,
            f"{prefix}_feature_description"
        )
        
        if desc_file:
            print(f"📋 Описание признаков сохранено: {desc_file}")
    
    def compare_scenarios_interactive(self):
        """Интерактивное сравнение сценариев"""
        print("\n🔄 СРАВНЕНИЕ СЦЕНАРИЕВ РАЗВИТИЯ")
        
        comparison = self.simulator.compare_scenarios()
        
        if len(comparison) == 0:
            print("❌ Не удалось сравнить сценарии.")
            return
        
        print("\n" + comparison.to_string(index=False))
        
        # Рекомендация
        if len(comparison) > 0:
            # Извлекаем числовые значения прибыли для сравнения
            def extract_profit(profit_str):
                try:
                    return float(profit_str.replace(' руб.', '').replace(',', ''))
                except:
                    return 0
            
            comparison['profit_num'] = comparison['Общая прибыль (30 дней)'].apply(extract_profit)
            best_idx = comparison['profit_num'].idxmax()
            best_scenario = comparison.iloc[best_idx]
            
            print(f"\n💡 РЕКОМЕНДАЦИЯ: {best_scenario['Сценарий']}")
            print(f"   Ожидаемая прибыль: {best_scenario['Общая прибыль (30 дней)']}")
    
    def run(self):
        """Запуск интерактивной панели"""
        print("\n" + "="*70)
        print("🚀 СИМУЛЯТОР УПРАВЛЕНИЯ КАФЕ С РЕКОМЕНДАЦИЯМИ В РЕАЛЬНОМ ВРЕМЕНИ")
        print("="*70)
        print("💡 Применяйте рекомендации и сразу видите их эффект на прогнозы!")
        print("💾 Данные автоматически сохраняются после каждого изменения")
        
        # Создаем структуру папок
        folders = ['datasets', 'forecasts', 'history', 'configs', 'reports', 'ml_data']
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Создана папка: {folder}/")
        
        while self.running:
            self.display_dashboard()
            self.show_recommendations()
            
            choice = input("\nВыберите действие (0-11): ").strip()
            
            if choice == '0':
                print("\n💾 Сохраняю финальные данные...")
                self.simulator.save_current_state("final_state")
                print("\nСпасибо за использование! До свидания! 👋")
                self.running = False
            
            elif choice == '1':
                self.apply_price_change()
            
            elif choice == '2':
                self.apply_promo_campaign()
            
            elif choice == '3':
                print("\n⏰ СЧАСТЛИВЫЕ ЧАСЫ")
                hours = input("Часы (например, 15-17): ")
                discount = input("Скидка (%): ")
                
                try:
                    params = {'hours': hours, 'discount': float(discount)}
                    effects = self.simulator.apply_recommendation('happy_hours', params)
                    print(f"\n✅ Применено: {effects['description']}")
                except:
                    print("❌ Ошибка ввода данных")
            
            elif choice == '4':
                print("\n📝 ИЗМЕНЕНИЕ МЕНЮ")
                print("1. Добавить блюдо")
                print("2. Удалить блюдо")
                
                subchoice = input("Выберите: ").strip()
                
                if subchoice == '1':
                    dish = input("Название нового блюда: ")
                    params = {'action': 'add', 'dish': dish}
                elif subchoice == '2':
                    dish = input("Название блюда для удаления: ")
                    params = {'action': 'remove', 'dish': dish}
                else:
                    print("❌ Неверный выбор")
                    continue
                
                effects = self.simulator.apply_recommendation('menu_change', params)
                print(f"\n✅ Применено: {effects['description']}")
            
            elif choice == '5':
                print("\n👑 УЛУЧШЕНИЕ ПРОГРАММЫ ЛОЯЛЬНОСТИ")
                improvement = input("Описание улучшения: ")
                params = {'improvement': improvement}
                
                effects = self.simulator.apply_recommendation('loyalty_program', params)
                print(f"\n✅ Применено: {effects['description']}")
            
            elif choice == '6':
                self.show_forecasts()
            
            elif choice == '7':
                self.compare_scenarios_interactive()
            
            elif choice == '8':
                print("\n💰 АНАЛИЗ ОКУПАЕМОСТИ ИНВЕСТИЦИЙ")
                
                try:
                    investment = float(input("Сумма инвестиций (руб.): "))
                    print("Тип инвестиций:")
                    print("1. Маркетинг")
                    print("2. Оборудование")
                    print("3. Обучение персонала")
                    
                    type_choice = input("Выберите тип: ").strip()
                    type_map = {'1': 'marketing', '2': 'equipment', '3': 'training'}
                    
                    if type_choice in type_map:
                        roi = self.simulator.generate_roi_analysis(investment, type_map[type_choice])
                        
                        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
                        print(f"  • Инвестиции: {roi['investment']:,.0f} руб.")
                        print(f"  • Ожидаемая доп. прибыль: {roi['additional_profit_expected']:,.0f} руб.")
                        print(f"  • ROI: {roi['roi_percent']:.1f}%")
                        print(f"  • Окупаемость: {roi['payback_months']:.1f} мес.")
                        print(f"  • Рекомендация: {roi['recommendation']}")
                    else:
                        print("❌ Неверный выбор")
                except:
                    print("❌ Ошибка ввода данных")
            
            elif choice == '9':
                print("\n📈 ИСТОРИЧЕСКИЕ ДАННЫЕ (последние 10 транзакций)")
                if len(self.historical_data) > 0:
                    cols_to_show = ['timestamp', 'dish_name', 'price', 'quantity', 'profit', 'client_id', 'promo_applied']
                    available_cols = [col for col in cols_to_show if col in self.historical_data.columns]
                    
                    if available_cols:
                        print(self.historical_data[available_cols].tail(10).to_string())
                    else:
                        print(self.historical_data.tail(10).to_string())
                    
                    print(f"\n📊 Статистика датасета:")
                    print(f"  • Всего строк: {len(self.historical_data)}")
                    print(f"  • Период: {self.historical_data['timestamp'].min()} - {self.historical_data['timestamp'].max()}")
                    print(f"  • Общая прибыль: {self.historical_data['profit'].sum():,.0f} руб.")
                    print(f"  • Средний чек: {self.historical_data['price'].mean():.0f} руб.")
                else:
                    print("Нет исторических данных")
            
            elif choice == '10':
                self.save_all_data()
            
            elif choice == '11':
                self.export_for_ml()
            
            else:
                print("❌ Неверный выбор, попробуйте снова")
            
            if choice != '0':
                input("\nНажмите Enter для продолжения...")

# ===================== ЗАПУСК СИСТЕМЫ =====================

if __name__ == "__main__":
    # Создаем дашборд и запускаем
    dashboard = RealTimeCafeDashboard()
    
    # Для быстрого теста можно запустить автоматический сценарий
    test_mode = input("Запустить тестовый сценарий? (да/нет): ").lower().strip()
    
    if test_mode in ['да', 'д', 'yes', 'y', '1']:
        print("\n🔧 ЗАПУСК ТЕСТОВОГО СЦЕНАРИЯ...")
        
        # Применяем несколько изменений
        dashboard.simulator.apply_recommendation('price_change', 
                                                {'category': 'coffee', 'change_pct': 10})
        dashboard.simulator.apply_recommendation('promo_campaign',
                                                {'discount': 15, 'duration': 7})
        
        print("\n✅ Тестовые изменения применены!")
        print("1. Цены на кофе увеличены на 10%")
        print("2. Запущена промо-кампания со скидкой 15%")
        
        # Показываем прогноз
        forecast = dashboard.simulator.get_forecast(30)
        if len(forecast) > 0:
            total_effect = forecast['predicted_profit'].sum() - (forecast['predicted_profit'].mean() * 30)
            print(f"\n📊 Ожидаемый эффект за 30 дней: {total_effect:+,.0f} руб.")
    
    # Запускаем интерактивную панель
    dashboard.run()