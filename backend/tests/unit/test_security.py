import pytest
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.crypto import encrypt_data, decrypt_data


def test_password_hashing():
    raw = "minhasenhasupersecreta"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("senhaerrada", hashed) is False


def test_jwt_token_generation_and_decoding():
    subject_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token(subject=subject_id)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == subject_id
    assert "exp" in payload


def test_aes_encryption_and_decryption():
    secret_text = "token_de_integracao_whatsapp_api_123456"
    encrypted = encrypt_data(secret_text)
    assert encrypted != secret_text
    decrypted = decrypt_data(encrypted)
    assert decrypted == secret_text
