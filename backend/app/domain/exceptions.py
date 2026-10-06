from typing import Any


class AppException(Exception):
    """Exceção base para todas as exceções de domínio da aplicação."""
    def __init__(self, message: str, status_code: int = 400, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class EntityNotFoundError(AppException):
    """Lançada quando uma entidade solicitada não existe no tenant."""
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} com identificador '{identifier}' não foi encontrado.",
            status_code=404,
        )


class EntityAlreadyExistsError(AppException):
    """Lançada quando já existe uma entidade com a mesma chave única."""
    def __init__(self, entity_name: str, field: str, value: Any):
        super().__init__(
            message=f"Já existe {entity_name} com {field} = '{value}'.",
            status_code=409,
        )


class BusinessRuleViolation(AppException):
    """Lançada quando uma operação viola regras de negócio."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, status_code=422, details=details)


class AppointmentConflictError(AppException):
    """Lançada quando ocorre colisão ou sobreposição de horários na agenda."""
    def __init__(self, message: str = "O horário selecionado não está mais disponível."):
        super().__init__(message=message, status_code=409)


class UnauthorizedError(AppException):
    """Lançada para credenciais inválidas ou ausência de autenticação."""
    def __init__(self, message: str = "Credenciais inválidas ou token expirado."):
        super().__init__(message=message, status_code=401)


class ForbiddenError(AppException):
    """Lançada quando o usuário não possui permissão para acessar o recurso do tenant."""
    def __init__(self, message: str = "Você não possui permissão para acessar este recurso."):
        super().__init__(message=message, status_code=403)
