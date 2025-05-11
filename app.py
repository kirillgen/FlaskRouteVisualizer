from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models.route_predictor import RoutePredictor

app = Flask(__name__)
CORS(app)

# Инициализация обработчика маршрутов
try:
    route_predictor = RoutePredictor()
except Exception as e:
    print(f"Ошибка инициализации: {str(e)}")
    route_predictor = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict_route', methods=['POST'])
def predict_route():
    if not route_predictor:
        print("Ошибка: сервис маршрутов недоступен")
        return jsonify({'error': 'Сервис маршрутов недоступен'}), 500
        
    data = request.json
    print(f"Получен запрос: {data}")
    if not data or 'start' not in data or 'end' not in data:
        print("Ошибка: не указаны начальная и конечная точки")
        return jsonify({'error': 'Необходимо указать начальную и конечную точки'}), 400
        
    start_point = data.get('start')
    end_point = data.get('end')
    route_type = data.get('route_type', 'car')
    
    # Получаем маршрут
    result = route_predictor.predict(start_point, end_point, route_type)
    print(f"Результат маршрута: {result}")
    
    if 'error' in result:
        return jsonify(result), 400
        
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 