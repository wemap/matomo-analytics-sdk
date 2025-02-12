import inspect
import requests

from .exceptions import MatomoAPIError, MatomoAuthError, MatomoRequestError
from .models import Config
from . import modules
from .modules import MatomoModule, CustomReports

HTTP_TIMEOUT_SECONDS = 10

# Dynamically discover all classes in the `modules.py` file
MODULES = [
    getattr(modules, name)
    for name, obj in inspect.getmembers(modules, inspect.isclass)
    # if issubclass(obj, MatomoModule)
    if obj is not MatomoModule
]


def to_snake_case(class_name: str) -> str:
    """
    Convert a class name like 'DevicesDetection' to 'devices_detection'
    without creating an instance.
    """
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in class_name]).lstrip(
        "_"
    )


class MatomoClient:
    """Main Matomo API client handling authentication and requests."""

    # TODO :
    # Add properties and serializers
    def __init__(self, config: Config):
        self.base_url = config.base_url.rstrip("/")
        self.site_id = config.site_id
        self.auth_token = config.auth_token
        self.format = config.format
        self.format_metrics = config.format_metrics
        self.filter_limit = config.filter_limit
        self.period = config.period
        self.date = config.date

        # Dynamically initialize all available modules
        self.modules = {
            to_snake_case(module.__name__): module(self) for module in MODULES
        }
        self.custom_reports = CustomReports(self)

    def __getattr__(self, name):
        """Allow accessing modules as attributes (e.g., client.events)."""
        if name in self.modules:
            return self.modules[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no module '{name}'")

    def _request(self, module: str, method: str, **kwargs) -> dict:
        """Generic request handler for Matomo API."""

        kwargs = {
            "module": "API",
            "method": f"{module}.{method}",
            "idSite": self.site_id,
            "token_auth": self.auth_token,
            "format": self.format,
            "period": self.period,
            "date": self.date,
        } | (kwargs or {})

        url = f"{self.base_url}/"
        try:
            response = requests.get(url, params=kwargs, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()
            if (
                isinstance(data, dict)
                and "result" in data
                and data["result"] == "error"
            ):
                if (
                    "message" in data
                    and "authentication failed" in data["message"].lower()
                ):
                    raise MatomoAuthError()
                raise MatomoAPIError(
                    data.get("message", "Unknown API error"), response.status_code
                )

            return data
        except requests.ConnectionError:
            raise MatomoRequestError("Failed to connect to Matomo server")
        except requests.Timeout:
            raise MatomoRequestError("Matomo request timed out")
        except requests.RequestException as e:
            raise MatomoRequestError(f"Matomo request failed: {e}")

    @classmethod
    def available_modules(cls):
        return [to_snake_case(module.__name__) for module in MODULES]
