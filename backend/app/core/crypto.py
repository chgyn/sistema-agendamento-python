import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings


def _get_aes_key() -> bytes:
    """Obtém ou deriva a chave de 32 bytes para AES-256-GCM a partir da configuração."""
    try:
        key = base64.b64decode(settings.AES_ENCRYPTION_KEY)
        if len(key) != 32:
            # Caso a chave decodificada não tenha 32 bytes, ajusta para 32 bytes de forma determinística
            return (key + b"0" * 32)[:32]
        return key
    except Exception:
        # Fallback determinístico caso o formato não seja base64 estrito
        return settings.SECRET_KEY.encode("utf-8")[:32].ljust(32, b"0")


def encrypt_data(plaintext: str) -> str:
    """Criptografa texto puro usando AES-256-GCM com nonce aleatório de 12 bytes.
    Retorna string codificada em base64 contendo nonce + ciphertext + tag.
    """
    if not plaintext:
        return ""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    payload = nonce + ciphertext
    return base64.b64encode(payload).decode("utf-8")


def decrypt_data(encrypted_text: str) -> str:
    """Descriptografa payload em base64 codificado com AES-256-GCM."""
    if not encrypted_text:
        return ""
    try:
        raw_payload = base64.b64decode(encrypted_text.encode("utf-8"))
        nonce = raw_payload[:12]
        ciphertext = raw_payload[12:]
        key = _get_aes_key()
        aesgcm = AESGCM(key)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_bytes.decode("utf-8")
    except Exception as exc:
        raise ValueError(f"Falha ao descriptografar dado sensível: {exc}") from exc
