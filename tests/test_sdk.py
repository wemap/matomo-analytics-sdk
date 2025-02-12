import requests
import responses
from responses import matchers

from src.matomo_analytics_sdk.client import MatomoClient
from src.matomo_analytics_sdk.models import Config
from src.matomo_analytics_sdk.exceptions import MatomoRequestError
from src.matomo_analytics_sdk.utils import read_json


def test_sdk_client():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token", period="day", date="today"
    )
    client = MatomoClient(config)
    assert client.base_url == config.base_url
    assert client.site_id == config.site_id
    assert client.auth_token == config.auth_token

    # defaults
    assert client.period == "day"
    assert client.date == "today"
    assert client.filter_limit == "100"
    assert client.format == "json"
    assert client.format_metrics == "0"


def test_get_module_methods():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token"
    )
    client = MatomoClient(config)

    events_methods = client.events.available_methods()
    devices_detection_methods = client.devices_detection.available_methods()
    referrers_methods = client.referrers.available_methods()
    user_country_methods = client.user_country.available_methods()
    segment_editor_methods = client.segment_editor.available_methods()

    assert sorted(events_methods) == [
        "getAction",
        "getActionFromCategoryId",
        "getActionFromNameId",
        "getCategory",
        "getCategoryFromActionId",
        "getCategoryFromNameId",
        "getName",
        "getNameFromActionId",
        "getNameFromCategoryId",
    ]
    assert sorted(devices_detection_methods) == [
        "getBrand",
        "getBrowserEngines",
        "getBrowserVersions",
        "getBrowsers",
        "getModel",
        "getOsFamilies",
        "getOsVersions",
        "getType",
    ]
    assert sorted(referrers_methods) == [
        "get",
        "getAll",
        "getCampaigns",
        "getKeywords",
        "getKeywordsFromCampaignId",
        "getKeywordsFromSearchEngineId",
        "getNumberOfDistinctCampaigns",
        "getNumberOfDistinctKeywords",
        "getNumberOfDistinctSearchEngines",
        "getNumberOfDistinctSocialNetworks",
        "getNumberOfDistinctWebsites",
        "getNumberOfDistinctWebsitesUrls",
        "getReferrerType",
        "getSearchEngines",
        "getSearchEnginesFromKeywordId",
        "getSocials",
        "getUrlsForSocial",
        "getUrlsFromWebsiteId",
        "getWebsites",
    ]
    assert sorted(user_country_methods) == [
        "getCity",
        "getContinent",
        "getCountry",
        "getCountryCodeMapping",
        "getLocationFromIP",
        "getNumberOfDistinctCountries",
        "getRegion",
        "setLocationProvider",
    ]
    assert sorted(segment_editor_methods) == [
        "add",
        "delete",
        "get",
        "getAll",
        "isUserCanAddNewSegment",
        "update",
    ]


@responses.activate
def test_events_get_name():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token", period="day", date="today"
    )
    client = MatomoClient(config)
    livemap = "16215"
    segment = f"dimension2=={livemap}"

    params = {
        "module": "API",
        "method": "Events.getName",
        "idSite": client.site_id,
        "token_auth": client.auth_token,
        "format": client.format,
        "period": client.period,
        "date": client.date,
        "segment": segment,
    }

    responses.add(
        responses.GET,
        client.base_url,
        match=[matchers.query_param_matcher(params)],
        json=read_json("tests/files/events_get_name.json"),
        status=200,
    )

    events = client.events.getName(segment=segment)

    assert len(events) == 59
    assert events[0]["label"] == "Nom d'\u00e9v\u00e8nement ind\u00e9fini"
    assert events[0]["nb_uniq_visitors"] == 23
    assert events[0]["nb_events"] == 1534
    assert events[0]["nb_events_with_value"] == 0
    assert events[0]["sum_event_value"] == 0
    assert events[0]["min_event_value"] == 0
    assert events[0]["max_event_value"] == 0
    assert events[0]["avg_event_value"] == 0
    assert events[0]["idsubdatatable"] == 1


def test_invalid_sdk_module():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token"
    )
    client = MatomoClient(config)
    try:
        events = client.HelloWorld
    except AttributeError as err:
        assert "'MatomoClient' has no module 'HelloWorld'" in str(err)


def test_invalid_events_method():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token"
    )
    client = MatomoClient(config)
    try:
        client.events.helloWorld()
    except AttributeError as err:
        assert "'Events' module has no method 'helloWorld'" in str(err)


def test_sdk_connection_error(mocker):
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token"
    )
    client = MatomoClient(config)

    mocker.patch("requests.get", side_effect=requests.ConnectionError)
    try:
        client.events.available_methods()
    except MatomoRequestError as err:
        assert "Failed to connect to Matomo server" in str(err)


def test_sdk_timeout_error(mocker):
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token"
    )
    client = MatomoClient(config)

    mocker.patch("requests.get", side_effect=requests.Timeout)
    try:
        client.events.available_methods()
    except MatomoRequestError as err:
        assert "Matomo request timed out" in str(err)


def test_sdk_request_exception(mocker):
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", auth_token="random_token"
    )
    client = MatomoClient(config)

    mocker.patch("requests.get", side_effect=requests.RequestException)
    try:
        client.events.available_methods()
    except MatomoRequestError as err:
        assert "Matomo request failed:" in str(err)
