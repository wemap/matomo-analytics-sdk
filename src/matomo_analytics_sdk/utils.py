import json
import os
import pkg_resources

import requests
from bs4 import BeautifulSoup


MATOMO_API_DOC_URL = "https://developer.matomo.org/api-reference/reporting-api"
MODULES_AND_METHODS = "files/available_modules.json"

def read_json(rel_path):
    resource_path = pkg_resources.resource_filename(
        'matomo_analytics_sdk', rel_path
    )
    with open(resource_path, "r") as file:
        return json.load(file)

def write_json(rel_path, data):
    abs_file_path = os.path.abspath(rel_path)
    with open(abs_file_path, "w") as file:
        json.dump(data, file, indent=4)


def fetch_modules_and_methods() -> dict:
    """Scrapes API methods from Matomo documentation."""
    response = requests.get(MATOMO_API_DOC_URL)
    if response.status_code != 200:
        raise RuntimeError("Failed to fetch Matomo API reference page")

    soup = BeautifulSoup(response.text, "html.parser")

    api_methods = {}

    # Extract all divs containing API methods
    for method_div in soup.find_all("div", class_="apiMethod"):
        bold_tag = method_div.find("b")
        if bold_tag:
            full_method_name = bold_tag.text.strip()
            if "." in full_method_name:
                module_name, method_name = full_method_name.split(".", 1)
                if module_name in api_methods:
                    api_methods[module_name].append(method_name)
                else:
                    api_methods[module_name] = [method_name]

    return api_methods


def available_modules() -> list:
    """Returns all available modules on Matomo API."""
    data = read_json(MODULES_AND_METHODS)
    return list(data.keys())


def available_methods(module_name: str) -> list:
    """Returns all available methods for a given module."""
    data = read_json(MODULES_AND_METHODS)
    return data.get(module_name, [])


def sync_modules_and_methods():
    old_data = read_json(MODULES_AND_METHODS)
    new_data = fetch_modules_and_methods()
    old_data.update(new_data)
    write_json(MODULES_AND_METHODS, old_data)
