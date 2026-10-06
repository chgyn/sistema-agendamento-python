import logging
from typing import Any
from celery import shared_task
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_confirmation(self, appointment_id: str) -> dict[str, Any]:
    """Tarefa assíncrona para envio de e-mail/notificação de confirmação de agendamento."""
    try:
        logger.info(f"[CELERY] Disparando confirmação para agendamento ID: {appointment_id}")
        # Aqui o worker pode integrar com serviços de e-mail (SendGrid/SES) ou WhatsApp (Z-API/Twilio)
        return {
            "status": "success",
            "appointment_id": appointment_id,
            "action": "confirmation_sent",
        }
    except Exception as exc:
        logger.error(f"[CELERY] Erro ao enviar confirmação para {appointment_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_cancellation(self, appointment_id: str, reason: str) -> dict[str, Any]:
    """Tarefa assíncrona para envio de notificação de cancelamento."""
    try:
        logger.info(f"[CELERY] Notificando cancelamento do agendamento {appointment_id}. Motivo: {reason}")
        return {
            "status": "success",
            "appointment_id": appointment_id,
            "reason": reason,
            "action": "cancellation_sent",
        }
    except Exception as exc:
        logger.error(f"[CELERY] Erro ao enviar cancelamento para {appointment_id}: {exc}")
        raise self.retry(exc=exc)
