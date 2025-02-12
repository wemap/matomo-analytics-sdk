from .utils import available_methods


class MatomoModule:
    """Generic Matomo module class that dynamically maps API methods."""

    def __init__(self, client):
        self.client = client
        self.module_name = self.__class__.__name__

    def available_methods(self):
        """Fetch available methods for this module from Matomo API."""
        if not self.client:
            raise ValueError("Client is not set for this module.")
        return available_methods(self.module_name)

    def __getattr__(self, method_name):
        """
        Dynamically call API methods.
        Raises AttributeError if method is not available.
        """
        if method_name not in available_methods(self.module_name):
            raise AttributeError(
                f"'{self.module_name}' module has no method '{method_name}'"
            )

        def api_method(**kwargs):
            return self.client._request(self.module_name, method_name, **kwargs)
        
        return api_method


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


class CustomReports:
    """Wemap custom reporting from aggregated data."""

    def __init__(self, client):
        self.client = client
        self.module_name = self.__class__.__name__

    def createCustomReport(self, **kwargs):
        pass

    def available_methods(self):
        pass
