import json
import os

import requests
import responses
from responses import matchers
from pydantic import ValidationError

from src.matomo_analytics_sdk.client import MatomoClient
from src.matomo_analytics_sdk.models import Config
from src.matomo_analytics_sdk.exceptions import MatomoRequestError


def read_json(rel_path):
    abs_file_path = os.path.abspath(rel_path)
    with open(abs_file_path, "r") as file:
        return json.load(file)


def test_client():
    config = Config(
        base_url="https://analytics.maaap.it",
        site_id="2",
        token_auth="random_token",
        period="day",
        date="today",
    )
    client = MatomoClient(config)

    # positionals
    assert client.base_url == config.base_url
    assert client.site_id == config.site_id
    assert client.token_auth == config.token_auth

    # defaults
    assert client.filter_limit == "100"
    assert client.format == "json"
    assert client.format_metrics == "0"

    livemap = 16215
    client.segment = f"dimension2=={livemap}"

    # Optionals
    assert client.period == "day"
    assert client.date == "today"
    assert client.segment == f"dimension2=={livemap}"


def test_missing_positional_param_in_client():
    try:
        # missing token_auth positional
        config = Config(
            base_url="https://analytics.maaap.it",
            site_id="2",
        )
    except ValidationError as err:
        assert "1 validation error for Config" in str(err)


def test_get_module_methods():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
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
        base_url="https://analytics.maaap.it",
        site_id="2",
        token_auth="random_token",
        period="day",
        date="2024-01-01,2024-01-02",
    )
    client = MatomoClient(config)
    livemap = "16215"
    segment = f"dimension2=={livemap}"

    params = {
        "module": "API",
        "method": "Events.getName",
        "idSite": client.site_id,
        "token_auth": client.token_auth,
        "format": client.format,
        "period": client.period,
        "date": client.date,
        "segment": segment,
    }

    responses.add(
        responses.POST,
        client.base_url,
        match=[matchers.urlencoded_params_matcher(params)],
        json=read_json("tests/files/Events_getName.json"),
        status=200,
    )

    events = client.events.getName(segment=segment)
    event_1 = events["2024-01-01"][1]
    assert len(events["2024-01-01"]) == 59
    assert event_1["label"] == "kiosk"
    assert event_1["nb_uniq_visitors"] == 4
    assert event_1["nb_visits"] == "25"
    assert event_1["nb_events"] == "694"
    assert event_1["nb_events_with_value"] == "694"
    assert event_1["sum_event_value"] == 2073
    assert event_1["min_event_value"] == 0
    assert event_1["max_event_value"] == 178
    assert event_1["avg_event_value"] == 2.99
    assert event_1["idsubdatatable"] == 2


@responses.activate
def test_wemap_custom_report():
    livemap = "16215"
    segment = f"dimension2=={livemap}"

    config = Config(
        base_url="https://analytics.maaap.it",
        site_id="2",
        token_auth="random_token",
        period="day",
        date="2024-01-01,2024-01-02",
        segment=segment,
    )
    client = MatomoClient(config)

    methods = {
        "API.get": {},
        "Events.getName": {},
        "Events.getAction": {},
        "Events.getCategory": {},
        "Referrers.getReferrerType": {},
        "DevicesDetection.getType": {},
        "UserCountry.getCity": {},
        "CustomDimensions.getCustomDimension": {"idDimension": 3},
    }

    for method, arguments in methods.items():
        params = {
            "module": "API",
            "method": method,
            "idSite": client.site_id,
            "token_auth": client.token_auth,
            "format": client.format,
            "period": client.period,
            "date": client.date,
            "segment": segment,
        }

        if method == "CustomDimensions.getCustomDimension":
            params.update({"idDimension": "3"})

        file_name = "_".join(method.split("."))

        responses.add(
            responses.POST,
            client.base_url,
            match=[matchers.urlencoded_params_matcher(params)],
            json=read_json(f"tests/files/{file_name}.json"),
            status=200,
        )

    wemap_reports = client.wemap_custom_reports
    new_report = wemap_reports.createReport(methods)

    assert True, {
        "Events",
        "API",
        "Referrers",
        "DevicesDetection",
        "UserCountry",
        "CustomDimensions",
    }.intersection(new_report.keys())

    assert new_report["Events"]["getName"]["2024-01-01"][1]["label"] == "kiosk"
    assert new_report["Events"]["getAction"]["2024-01-01"][0]["label"] == "update"
    assert new_report["API"]["get"]["2024-01-01"]["nb_uniq_visitors"] == 5
    assert (
        new_report["Referrers"]["getReferrerType"]["2024-01-01"][0]["label"]
        == "Entr\u00e9es directes"
    )
    assert (
        new_report["DevicesDetection"]["getType"]["2024-01-01"][0]["label"]
        == "Tablette"
    )
    assert (
        new_report["UserCountry"]["getCity"]["2024-01-01"][0]["label"]
        == "Marseille, France"
    )
    assert (
        new_report["CustomDimensions"]["getCustomDimension"]["2024-01-01"][0]["label"]
        == "hdv_direction_gare"
    )


def test_protected_keys():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
    )
    client = MatomoClient(config)
    methods = {
        "Events.getName": {"base_url": "https://google.com", "token_auth": "12345"},
    }

    wemap_reports = client.wemap_custom_reports
    try:
        new_report = wemap_reports.createReport(methods)
    except ValueError as err:
        assert "base_url parameter cannot be modified." in str(err)


def test_invalid_module():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
    )
    client = MatomoClient(config)
    try:
        events = client.HelloWorld
    except AttributeError as err:
        assert "'MatomoClient' has no module 'HelloWorld'" in str(err)


def test_invalid_events_method():
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
    )
    client = MatomoClient(config)
    try:
        client.events.helloWorld()
    except AttributeError as err:
        assert "'Events' module has no method 'helloWorld'" in str(err)


def test_connection_error(mocker):
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
    )
    client = MatomoClient(config)

    mocker.patch("requests.get", side_effect=requests.ConnectionError)
    try:
        client.events.available_methods()
    except MatomoRequestError as err:
        assert "Failed to connect to Matomo server" in str(err)


def test_timeout_error(mocker):
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
    )
    client = MatomoClient(config)

    mocker.patch("requests.get", side_effect=requests.Timeout)
    try:
        client.events.available_methods()
    except MatomoRequestError as err:
        assert "Matomo request timed out" in str(err)


def test_request_exception(mocker):
    config = Config(
        base_url="https://analytics.maaap.it", site_id="2", token_auth="random_token"
    )
    client = MatomoClient(config)

    mocker.patch("requests.get", side_effect=requests.RequestException)
    try:
        client.events.available_methods()
    except MatomoRequestError as err:
        assert "Matomo request failed:" in str(err)
