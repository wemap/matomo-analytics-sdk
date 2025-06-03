# Wemap Analytics SDK
-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install .
```
or 

```console
pip install https://github.com/wemap/matomo-analytics-sdk/releases/download/v1.0.0/matomo_analytics_sdk-0.0.1-py3-none-any.whl
```

## Quick Start

### 1. Initialize the Client

```python
from matomo_analytics_sdk.client import MatomoClient
from matomo_analytics_sdk.models import Config

config = Config(
    base_url="https://your-matomo-instance.com",
    site_id="1",
    token_auth="your_api_token"
)

client = MatomoClient(config)
```

### 2. Fetch Available Modules

```python
print(client.available_modules())
```

### 3. Retrieve Data (Example: Fetching Events Data)

```python
response = client.events.getCategory()
print(response)
```

You can also fetch available methods for each module

```python
response = client.events.available_methods()
print(response)
```

## Modules & Methods

The SDK dynamically loads available Matomo modules. You can call any method provided by Matomo's API via the SDK:

```python
client.referrers.getKeywords()
client.user_country.getCountry()
```

### Wemap Custom Reports

You can create custom reports by aggregating multiple API responses:

```python
metrics = {
    "VisitsSummary.get": {},
    "Actions.get": {}
}
response = client.wemap_custom_reports.getReport(metrics=metrics)
```

## Error Handling

The SDK includes custom exceptions:

- `MatomoAPIError`: Raised when Matomo API returns an error.
- `MatomoAuthError`: Raised on authentication failures.
- `MatomoRequestError`: Raised on network or request issues.
- `MatomoValidationError`: Raised for invalid parameters.


## License

`matomo-analytics-sdk` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
