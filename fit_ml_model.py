import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
import os
import matplotlib.pyplot as plt

# Загрузка данных
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, 'route_training_data.csv')
data = pd.read_csv(data_path)

# Выбор признаков и целевой переменной
X = data[['points_count', 'local_duration', 'distance']].values
y = data['api_duration'].values
print(data.head())

# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Добавление полиномиальных признаков
poly = PolynomialFeatures(degree=5, include_bias=False)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Получение имен полиномиальных признаков
feature_names = ['points_count', 'local_duration', 'distance']
poly_feature_names = poly.get_feature_names_out(feature_names)

# Создание и обучение модели дерева решений
model = DecisionTreeRegressor(random_state=42, max_depth=5, min_samples_split=10)
model.fit(X_train_poly, y_train)

# Предсказание на тестовой выборке
y_pred = model.predict(X_test_poly)

# Оценка качества модели
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Вывод результатов
print(f'Среднеквадратичная ошибка: {mse}')
print(f'Коэффициент детерминации (R²): {r2}')
print(f'Score: {model.score(X_test_poly, y_test)}')

# Визуализация результатов
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel('Фактическое значение')
plt.ylabel('Предсказанное значение')
plt.title('Фактическое vs Предсказанное значение api_duration')
plt.savefig('prediction_plot.png')

# Важность признаков
importance = pd.DataFrame({
    'Признак': poly_feature_names,
    'Важность': model.feature_importances_
})
print('\nВажность признаков:')
print(importance.sort_values(by='Важность', ascending=False))

# Визуализация важности признаков
plt.figure(figsize=(12, 8))
importance_sorted = importance.sort_values('Важность', ascending=False)
plt.barh(importance_sorted['Признак'], importance_sorted['Важность'])
plt.xlabel('Важность')
plt.title('Важность признаков')
plt.tight_layout()
plt.savefig('feature_importance.png')