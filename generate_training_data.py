import os
import random
import pandas as pd
import numpy as np
from models.route_predictor import RoutePredictor
from tqdm import tqdm
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Границы для Лихтенштейна (примерные координаты)
# Можно уточнить границы, если нужно более точное ограничение
LIECHTENSTEIN_BOUNDS = {
    'min_lat': 47.15416,    
    'max_lat': 47.17791,
    'min_lon': 9.507852,
    'max_lon': 9.510591
}



def generate_random_point():
    """Генерация случайной точки в пределах Лихтенштейна"""
    lat = random.uniform(LIECHTENSTEIN_BOUNDS['min_lat'], LIECHTENSTEIN_BOUNDS['max_lat'])
    lon = random.uniform(LIECHTENSTEIN_BOUNDS['min_lon'], LIECHTENSTEIN_BOUNDS['max_lon'])
    return (lat, lon)

def extract_route_features(route_data):
    """Извлечение характеристик маршрута из результата предсказания"""
    features = {
        'distance': route_data['distance'],
        'local_duration': route_data['duration']['local'],
        'api_duration': route_data['duration']['api'],
        'selected_duration': route_data['duration']['selected'],
        'route_type': route_data['route_type'],
        'points_count': len(route_data['route']),
    }
    
    # Здесь можно добавить дополнительные характеристики маршрута, 
    # если они доступны через API route_predictor
    
    return features

def generate_dataset(samples=100, output_file='route_training_data.csv'):
    """Основная функция для генерации датасета"""
    print(f"Инициализация RoutePredictor...")
    route_predictor = RoutePredictor()
    
    # Создаем DataFrame для хранения данных
    columns = [
        'start_lat', 'start_lon', 
        'end_lat', 'end_lon',
        'distance', 
        'local_duration', 
        'api_duration', 
        'selected_duration',
        'route_type',
        'points_count'
    ]
    
    # Проверяем, существует ли уже файл
    if os.path.exists(output_file):
        print(f"Файл {output_file} уже существует, продолжаем добавлять данные...")
        df = pd.read_csv(output_file)
    else:
        print(f"Создаем новый файл {output_file}...")
        df = pd.DataFrame(columns=columns)
    
    route_types = ['car']
    
    successful_routes = 0
    attempts = 0
    max_attempts = samples * 3  # Максимальное количество попыток
    
    with tqdm(total=samples) as pbar:
        while successful_routes < samples and attempts < max_attempts:
            try:
                # Увеличиваем счетчик попыток
                attempts += 1
                
                # Генерируем случайные точки
                start_point = generate_random_point()
                end_point = generate_random_point()
                
                # Выбираем случайный тип маршрута
                route_type = random.choice(route_types)
                
                print(f"\nПопытка {attempts}: построение маршрута от {start_point} до {end_point} ({route_type})")
                
                # Строим маршрут
                result = route_predictor.predict(start_point, end_point, route_type)
                
                # Проверяем, успешно ли построен маршрут
                if 'error' in result:
                    print(f"Ошибка: {result['error']}")
                    continue
                
                # Если API вернул None для duration, пропускаем эту пару точек
                if result['duration']['api'] is None:
                    print("API не вернул время для маршрута, пропускаем...")
                    continue
                
                # Извлекаем характеристики маршрута
                features = extract_route_features(result)
                
                # Создаем запись для датасета
                record = {
                    'start_lat': start_point[0],
                    'start_lon': start_point[1],
                    'end_lat': end_point[0],
                    'end_lon': end_point[1],
                    **features
                }
                
                # Добавляем запись в DataFrame
                df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
                
                # Сохраняем после каждой успешной записи
                df.to_csv(output_file, index=False)
                
                successful_routes += 1
                pbar.update(1)
                print(f"Успешно добавлена запись {successful_routes}/{samples}")
                
            except Exception as e:
                print(f"Непредвиденная ошибка: {str(e)}")
                continue
    
    print(f"\nГенерация данных завершена!")
    print(f"Успешно сгенерировано {successful_routes} маршрутов из {samples} запланированных")
    print(f"Данные сохранены в файл: {output_file}")
    
    return df

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Генерация данных для обучения ML модели предсказания времени маршрута')
    parser.add_argument('--samples', type=int, default=100, help='Количество образцов для генерации')
    parser.add_argument('--output', type=str, default='route_training_data.csv', help='Имя выходного файла')
    
    args = parser.parse_args()
    
    print(f"Запуск генерации {args.samples} маршрутов...")
    generate_dataset(samples=args.samples, output_file=args.output) 