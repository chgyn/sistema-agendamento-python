from datetime import date, timedelta
import pytest
from app.services.availability_service import AvailabilityService


@pytest.mark.asyncio
async def test_availability_calculation_and_break_time(db_session, sample_setup):
    service = sample_setup["service"]
    professional = sample_setup["professional"]
    establishment = sample_setup["establishment"]

    availability_service = AvailabilityService()

    # Busca a próxima segunda-feira para teste consistente
    today = date.today()
    days_ahead = (0 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    target_date = today + timedelta(days=days_ahead)

    result = await availability_service.get_available_slots(
        session=db_session,
        slug=establishment.slug,
        professional_id=professional.id,
        service_id=service.id,
        target_date=target_date,
    )

    assert result.date == target_date
    assert len(result.slots) > 0

    # Verifica slot das 09:00
    slot_9am = next((s for s in result.slots if s.start_time == "09:00"), None)
    assert slot_9am is not None
    assert slot_9am.is_available is True

    # Verifica que o horário do almoço (12:00 às 13:00) está marcado como indisponível
    slot_lunch = next((s for s in result.slots if s.start_time == "12:00"), None)
    assert slot_lunch is not None
    assert slot_lunch.is_available is False


@pytest.mark.asyncio
async def test_availability_on_day_without_work(db_session, sample_setup):
    service = sample_setup["service"]
    professional = sample_setup["professional"]
    establishment = sample_setup["establishment"]

    availability_service = AvailabilityService()

    # Busca o próximo domingo (dia 6, sem grade cadastrada no setup)
    today = date.today()
    days_ahead = (6 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    sunday_date = today + timedelta(days=days_ahead)

    result = await availability_service.get_available_slots(
        session=db_session,
        slug=establishment.slug,
        professional_id=professional.id,
        service_id=service.id,
        target_date=sunday_date,
    )

    assert len(result.slots) == 0
