import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

# ✅ Подключение к базе данных
def connect():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("✅ Подключение к базе данных установлено")
            return conn
    except Error as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None

# ✅ Добавление данных
def add_progress(user_id, exercise, category, reps, weight, date):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            query = '''
                INSERT INTO progress (user_id, exercise, category, reps, weight, date)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(query, (user_id, exercise, category, reps, weight, date))
            conn.commit()
            cursor.close()
            print("✅ Данные успешно сохранены в базу данных")
        except Error as e:
            print(f"❌ Ошибка при сохранении в базу данных: {e}")
        finally:
            conn.close()

# ✅ Получение данных
def get_progress(user_id):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            query = '''
                SELECT id, category, exercise, reps, weight, date 
                FROM progress 
                WHERE user_id = %s
                ORDER BY date DESC
            '''
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            print(f"❌ Ошибка при получении данных из базы: {e}")
        finally:
            conn.close()
    return []

# ✅ УДАЛЕНИЕ данных
def delete_progress(record_id):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            query = 'DELETE FROM progress WHERE id = %s'
            cursor.execute(query, (record_id,))
            conn.commit()
            cursor.close()
            print(f"✅ Запись {record_id} успешно удалена")
        except Error as e:
            print(f"❌ Ошибка при удалении записи: {e}")
        finally:
            conn.close()

def convert_date(date_str):
    day, month, year = date_str.split('.')
    return f"{year}-{month}-{day}"

# ✅ ОБНОВЛЕНИЕ данных с категорией
def update_progress(workout_id, category, exercise, reps, weight, date):
    conn = connect()
    if conn:
        try:
            cursor = conn.cursor()
            query = '''
                UPDATE progress
                SET category = %s, exercise = %s, reps = %s, weight = %s, date = %s
                WHERE id = %s
            '''
            cursor.execute(query, (category, exercise, reps, weight, date, workout_id))
            conn.commit()
            cursor.close()
            print(f"✅ Тренировка с ID {workout_id} успешно обновлена!")
        except Error as e:
            print(f"❌ Ошибка при обновлении данных: {e}")
        finally:
            conn.close()

# ✅ Экспортируем функции для импорта в другие модули
__all__ = ["add_progress", "get_progress", "delete_progress", "update_progress"]