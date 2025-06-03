import logging
from .utils import available_methods

logger = logging.getLogger(__name__)


class MatomoModule:
    """Generic Matomo module class that dynamically maps API methods."""

    def __init__(self, client):
        self.client = client
        self.module_name = self.__class__.__name__

        logger.debug(f"Module '{self.module_name}' initialized.")

    def available_methods(self):
        if not self.client:
            raise ValueError("Client is not set for this module.")
        return available_methods(self.module_name)

    def __getattr__(self, method_name):
        """Dynamically call API methods."""

        if method_name not in available_methods(self.module_name):
            raise AttributeError(
                f"'{self.module_name}' module has no method '{method_name}'"
            )

        def api_method(**kwargs):
            logger.debug(
                f"Calling method '{method_name}' on module '{self.module_name}' with params: {kwargs}"
            )
            return self.client._request(self.module_name, method_name, **kwargs)

        return api_method


class WemapCustomReports(MatomoModule):
    """Wemap custom reporting from aggregated data."""

    def getReport(self, metrics):
        if not metrics or not isinstance(metrics, list):
            raise ValueError("Expected a non-empty list of metric definitions.")

        report = []

        for metric in metrics:
            method = metric.get("method")
            if not method:
                raise ValueError("Each metric must include a 'method' key.")

            module_name, method_name = method.split(".")

            if method_name not in available_methods(module_name):
                raise AttributeError(f"'{module_name}' module has no method '{method_name}'")

            # Extract kwargs to pass to the actual request
            kwargs = {k: v for k, v in metric.items() if k != "method"}

            # Perform request
            response = self.client._request(module_name, method_name, **kwargs)

            # Add response to unified report format
            report.append({
                "method": method,
                **kwargs,  # this will include period, date, segment, etc.
                "data": response
            })

        return {"report": report}

    def available_methods(self):
        """List public methods defined in this subclass."""
        return [
            method
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("_")
            and method not in dir(MatomoModule)
        ]


class API(MatomoModule):
    """This API is the Metadata API: it gives information about all other available APIs methods, as well as providing human readable and more complete outputs than normal API methods."""

    pass


class DevicesDetection(MatomoModule):
    """The DevicesDetection API lets you access reports on your visitors devices, brands, models, Operating system, Browsers."""

    pass


class Events(MatomoModule):
    """The Events API lets you request reports about your users' Custom Events."""

    pass


class Referrers(MatomoModule):
    """The Referrers API lets you access reports about Websites, Search engines, Keywords, Campaigns used to access your website."""

    pass


class UserCountry(MatomoModule):
    """The UserCountry API lets you access reports about your visitors' Countries and Continents."""

    pass


class SegmentEditor(MatomoModule):
    """The SegmentEditor API lets you add, update, delete custom Segments, and list saved segments."""

    pass


class CustomDimensions(MatomoModule):
    "The Custom Dimensions API lets you manage and access reports for your configured Custom Dimensions."

    pass
