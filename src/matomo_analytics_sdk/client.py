import inspect
import requests

from .exceptions import MatomoAPIError, MatomoAuthError, MatomoRequestError
from .models import Config
from . import modules
from .modules import MatomoModule

HTTP_TIMEOUT_SECONDS = 10
PROTECTED_KEYS = {"base_url", "site_id", "token_auth"}
# Dynamically discover all classes in the `modules.py` file
MODULES = [
    getattr(modules, name)
    for name, obj in inspect.getmembers(modules, inspect.isclass)
    if obj is not MatomoModule
]


def to_snake_case(class_name: str) -> str:
    """
    Convert a class name like 'DevicesDetection' to 'devices_detection'
    without creating an instance.
    """
    if class_name.isupper():
        return class_name.lower()

    return "".join([f"_{c.lower()}" if c.isupper() else c for c in class_name]).lstrip(
        "_"
    )


class MatomoClient:
    """Main Matomo API client handling authentication and requests."""

    def __init__(self, config: Config):
        self.base_url = config.base_url.rstrip("/")
        self.site_id = config.site_id
        self.token_auth = config.token_auth
        self.format = config.format
        self.format_metrics = config.format_metrics
        self.filter_limit = config.filter_limit
        self.period = config.period
        self.date = config.date
        self.segment = config.segment

        # Dynamically initialize all available modules
        self.modules = {
            to_snake_case(module.__name__): module(self) for module in MODULES
        }

    def __getattr__(self, name):
        """Allow accessing modules as attributes (e.g., client.events)."""
        if name in self.modules:
            return self.modules[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no module '{name}'")

    def _request(self, module: str, method: str, **kwargs) -> dict:
        """Generic request handler for Matomo API."""

        params = {
            "module": "API",
            "method": f"{module}.{method}",
            "idSite": self.site_id,
            "token_auth": self.token_auth,
            "format": self.format,
            "period": self.period,
            "date": self.date,
            "segment": self.segment,
        }

        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key in PROTECTED_KEYS:
                raise ValueError(f"{key} parameter cannot be modified.")
            else:
                filtered_kwargs[key] = value

        params.update(filtered_kwargs)

        url = f"{self.base_url}/"
        try:
            response = requests.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
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
