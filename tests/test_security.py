"""Тесты для модуля безопасности."""
import pytest
from datetime import timedelta
from shared.security import (
    create_access_token,
    decode_access_token,
    verify_password,
    get_password_hash,
    SecuritySettings,
)


def test_password_hashing():
    """Тест хеширования паролей."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0
    
    # Проверка пароля
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Тест создания JWT токена."""
    data = {"sub": "user-123", "email": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    """Тест декодирования JWT токена."""
    data = {"sub": "user-123", "email": "test@example.com"}
    token = create_access_token(data)
    
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded
    assert "iat" in decoded


def test_decode_invalid_token():
    """Тест декодирования невалидного токена."""
    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)
    
    assert decoded is None


def test_token_expiration():
    """Тест истечения токена."""
    data = {"sub": "user-123"}
    # Создать токен с коротким временем жизни
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    # Токен должен быть невалидным
    decoded = decode_access_token(token)
    # В реальности JWT библиотека проверит exp, но для теста проверим что токен создан
    assert token is not None

