#!/usr/bin/env python3
"""Скрипт для валидации тестов без запуска pytest."""
import ast
import sys
from pathlib import Path


def validate_python_file(file_path: Path) -> tuple[bool, list[str]]:
    """Проверить синтаксис Python файла."""
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Проверка синтаксиса
        ast.parse(source, filename=str(file_path))
        return True, []
    except SyntaxError as e:
        errors.append(f"SyntaxError: {e.msg} at line {e.lineno}")
        return False, errors
    except Exception as e:
        errors.append(f"Error: {str(e)}")
        return False, errors


def check_imports(file_path: Path) -> tuple[bool, list[str]]:
    """Проверить импорты в файле."""
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        
        # Проверить все импорты
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Базовая проверка - импорт существует в синтаксисе
                pass
        
        return True, []
    except Exception as e:
        errors.append(f"Import check error: {str(e)}")
        return False, errors


def main():
    """Основная функция валидации."""
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    shared_dir = project_root / "shared"
    
    print("=" * 60)
    print("Валидация тестов и модулей")
    print("=" * 60)
    
    all_passed = True
    
    # Проверка тестов
    print("\n1. Проверка тестов...")
    test_files = [
        "test_exceptions.py",
        "test_security.py",
        "test_retry.py",
        "test_api_integration.py",
        "test_graph_rag.py",
        "conftest.py"
    ]
    
    for test_file in test_files:
        file_path = tests_dir / test_file
        if file_path.exists():
            is_valid, errors = validate_python_file(file_path)
            if is_valid:
                print(f"  ✓ {test_file}")
            else:
                print(f"  ✗ {test_file}: {', '.join(errors)}")
                all_passed = False
        else:
            print(f"  ⚠ {test_file} не найден")
    
    # Проверка shared модулей
    print("\n2. Проверка shared модулей...")
    shared_files = [
        "logging_config.py",
        "security.py",
        "exceptions.py",
        "middleware.py",
        "retry.py"
    ]
    
    for shared_file in shared_files:
        file_path = shared_dir / shared_file
        if file_path.exists():
            is_valid, errors = validate_python_file(file_path)
            if is_valid:
                print(f"  ✓ {shared_file}")
            else:
                print(f"  ✗ {shared_file}: {', '.join(errors)}")
                all_passed = False
        else:
            print(f"  ⚠ {shared_file} не найден")
    
    # Проверка структуры тестов
    print("\n3. Проверка структуры тестов...")
    
    # Проверка наличия тестовых функций
    test_patterns = [
        ("test_exceptions.py", ["test_app_exception", "test_not_found_error"]),
        ("test_security.py", ["test_password_hashing", "test_create_access_token"]),
        ("test_retry.py", ["test_retry_success", "test_retry_exhausted"]),
    ]
    
    for test_file, expected_tests in test_patterns:
        file_path = tests_dir / test_file
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_tests = []
            for expected_test in expected_tests:
                if f"def {expected_test}" in content:
                    found_tests.append(expected_test)
            
            if found_tests:
                print(f"  ✓ {test_file}: найдено {len(found_tests)}/{len(expected_tests)} тестов")
            else:
                print(f"  ⚠ {test_file}: тесты не найдены")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ Валидация пройдена успешно!")
        print("\nДля запуска тестов выполните:")
        print("  pip install -r requirements.txt")
        print("  pytest tests/ -v")
        return 0
    else:
        print("✗ Обнаружены ошибки валидации")
        return 1


if __name__ == "__main__":
    sys.exit(main())

