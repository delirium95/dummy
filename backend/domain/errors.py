class DomainError(Exception):
    """Base class for all domain-level errors."""


class NotFoundError(LookupError, DomainError):
    """Raised when an aggregate is not found."""


class ConflictError(DomainError):
    """Raised when a write would violate a domain invariant or uniqueness rule."""


class ValidationError(ValueError, DomainError):
    """Raised when input fails domain validation."""


class EmailAlreadyExistsError(ConflictError):
    pass


class UsernameAlreadyExistsError(ConflictError):
    pass


class NotFoundUserError(NotFoundError):
    pass


class NotFoundPostError(NotFoundError):
    pass


class PostAuthorNotFoundError(NotFoundError):
    pass


class ExternalSourceError(DomainError):
    pass


class ExternalSourceTimeoutError(ExternalSourceError):
    pass


class ExternalSourceUnavailableError(ExternalSourceError):
    pass


class ExternalSourcePayloadError(ExternalSourceError):
    pass
