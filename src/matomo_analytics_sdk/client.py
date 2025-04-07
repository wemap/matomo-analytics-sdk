import inspect
import requests
import logging

from .exceptions import MatomoAPIError, MatomoAuthError, MatomoRequestError
from .models import Config
from . import modules
from .modules import MatomoModule

HTTP_TIMEOUT_SECONDS = 10
PROTECTED_KEYS = {"base_url", "token_auth"}

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Dynamically discover all classes in the `modules.py` file
MODULES = [
    getattr(modules, name)
    for name, obj in inspect.getmembers(modules, inspect.isclass)
    if obj is not MatomoModule
]


def to_snake_case(class_name: str) -> str:
    if class_name.isupper():
        return class_name.lower()
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in class_name]).lstrip(
        "_"
    )


class MatomoClient:
    """Main Matomo API client handling authentication and requests."""

    def __init__(self, config: Config, verbose=False):
        self.base_url = config.base_url.rstrip("/")
        self.site_id = config.site_id
        self.token_auth = config.token_auth
        self.format = config.format
        self.format_metrics = config.format_metrics
        self.filter_limit = config.filter_limit
        self.period = config.period
        self.date = config.date
        self.segment = config.segment
        self.verbose = verbose
        self._config = config

        if verbose:
            logger.setLevel(logging.DEBUG)

        logger.info("MatomoClient initialized.")

        # Dynamically initialize all available modules
        self.modules = {
            to_snake_case(module.__name__): module(self) for module in MODULES
        }
    
    @property
    def config(self):
        return self._config

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self.modules:
            return self.modules[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no module '{name}'")

    def _request(self, module: str, method: str, **kwargs) -> dict:
        """Generic request handler for Matomo API."""

        data = {
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
            filtered_kwargs[key] = value

        data.update(filtered_kwargs)

        url = f"{self.base_url}/"

        logger.debug(f"Sending request to {url} with data: {data}")

        try:
            response = requests.post(url, data=data, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Response received: {data}")

            if isinstance(data, dict) and data.get("result") == "error":
                if "authentication failed" in data.get("message", "").lower():
                    logger.error("Authentication error.")
                    raise MatomoAuthError()
                logger.error(
                    f"Matomo API error: {data.get('message', 'Unknown error')}"
                )
                raise MatomoAPIError(
                    data.get("message", "Unknown API error"), response.status_code
                )

            return data
        except requests.ConnectionError:
            err_msg = "Failed to connect to Matomo server"
            logger.error(err_msg)
            raise MatomoRequestError(err_msg)
        except requests.Timeout:
            err_msg = "Matomo request timed out"
            logger.error(err_msg)
            raise MatomoRequestError(err_msg)
        except requests.RequestException as e:
            err_msg = "Matomo request failed:"
            logger.error(f"{err_msg} {e}")
            raise MatomoRequestError(f"{err_msg} {e}")

    @classmethod
    def available_modules(cls):
        return [to_snake_case(module.__name__) for module in MODULES]
