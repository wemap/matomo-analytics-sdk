class MatomoError(Exception):
    """Base class for all Matomo SDK exceptions."""

    pass


class MatomoAPIError(MatomoError):
    """Exception raised when the Matomo API returns an error response."""

    def __init__(
        self, message="Matomo API error", status_code=None, response_data=None
    ):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(f"{message} (Status Code: {status_code})")


class MatomoAuthError(MatomoAPIError):
    """Exception raised when there is an authentication error with Matomo."""

    def __init__(self, message="Invalid Matomo authentication token"):
        super().__init__(message, status_code=401)


class MatomoRequestError(MatomoError):
    """Exception raised when there is a network or request-related issue."""

    def __init__(self, message="Failed to connect to Matomo server"):
        super().__init__(message)


class MatomoValidationError(MatomoError):
    """Exception raised when invalid data is provided to the SDK."""

    def __init__(self, message="Invalid parameters provided to Matomo SDK"):
        super().__init__(message)
