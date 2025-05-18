from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models.route_predictor import RoutePredictor
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)
CORS(app)

print("Инициализация приложения...")

# Инициализация обработчика маршрутов
try:
    print("Создаю экземпляр RoutePredictor...")
    route_predictor = RoutePredictor()
    print("RoutePredictor успешно создан")
except Exception as e:
    print(f"Ошибка инициализации RoutePredictor: {str(e)}")
    route_predictor = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict_route', methods=['POST'])
def predict_route():
    print("\n=== Новый запрос на построение маршрута ===")
    
    if not route_predictor:
        print("Ошибка: сервис маршрутов недоступен")
        return jsonify({'error': 'Сервис маршрутов недоступен'}), 500
        
    data = request.json
    print(f"Получены данные: {data}")
    
    if not data or 'start' not in data or 'end' not in data:
        print("Ошибка: не указаны начальная и конечная точки")
        return jsonify({'error': 'Необходимо указать начальную и конечную точки'}), 400
        
    start_point = data.get('start')
    end_point = data.get('end')
    route_type = data.get('route_type', 'car')
    
    print(f"Начальная точка: {start_point}")
    print(f"Конечная точка: {end_point}")
    print(f"Тип маршрута: {route_type}")
    
    # Получаем маршрут
    try:
        print("Запускаю построение маршрута...")
        result = route_predictor.predict(start_point, end_point, route_type)
        print(f"Получен результат: {result}")
        
        if 'error' in result:
            print(f"Ошибка при построении: {result['error']}")
            return jsonify(result), 400
            
        print("Маршрут успешно построен")
        return jsonify(result)
    except Exception as e:
        error_msg = f"Неожиданная ошибка при построении маршрута: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True) 