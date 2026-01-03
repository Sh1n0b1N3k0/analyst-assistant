"""Python скрипт для инициализации базы данных."""
import os
import sys
from pathlib import Path

def init_database_from_sql():
    """Инициализация базы данных из SQL файла."""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from config import settings
    
    # Читаем SQL файл
    sql_file = Path(__file__).parent / "init_database.sql"
    
    if not sql_file.exists():
        print(f"✗ Файл {sql_file} не найден!")
        sys.exit(1)
    
    try:
        # Подключение к базе данных
        print("Подключение к базе данных...")
        conn = psycopg2.connect(settings.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Читаем и выполняем SQL скрипт
        print(f"Чтение SQL файла: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("Выполнение SQL скрипта...")
        cursor.execute(sql_script)
        
        print("✓ База данных успешно инициализирована!")
        print(f"  Версия схемы: 1.4.1")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"✗ Ошибка при инициализации базы данных: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Инициализация базы данных для системы управления требованиями")
    print("=" * 60)
    print()
    
    # Проверка наличия config
    try:
        from config import settings
    except ImportError:
        print("✗ Модуль config не найден!")
        print("  Создайте файл config.py с настройками базы данных")
        sys.exit(1)
    
    init_database_from_sql()

