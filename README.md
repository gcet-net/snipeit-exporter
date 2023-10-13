# Snipe-IT Exporter
Snipe-IT exporter for [prometheus](https://prometheus.io), written in Python.

## Background
This exporter was designed to monitor asset counts by status in an environment where the asset status changes daily. Assets can be monitored by simply changing the asset category in Snipe-IT.

## Features
The following metrics are currently supported:

* Asset counts by status `labels=['name', 'model_number', 'status']`
* Asset counts by user `labels=['user', 'name','model_number']`
* Consumable remaining quantity `labels=['name', 'model_number']`
* Component remaining quantity `labels=['name', 'serial']`

>**NOTE:** Asset counts by user, Consumables and Component remaining quantity are disabled by default.

### Assets
Metric counts of assets are grouped by status names. Asset model must be configured with a category and the category name passed to exporter with the `--asset_categories` argument. To avoid performance issues the export requires assets to be filtered by category and status names. The more statuses to filter the longer polling time. This maybe viewed as limiting factor.

### User Assets
Metric counts of assets assigned to user are limited by asset category names. This means only filtered assets will be counted NOT all user assigned assets.  

## Usage

```shell
python snipeit_exporter.py --h
usage: snipeit_exporter.py [-h] --apikey APIKEY --target TARGET [--port PORT] [--asset_statuses ASSET_STATUSES [ASSET_STATUSES ...]]
                           [--asset_categories ASSET_CATEGORIES [ASSET_CATEGORIES ...]] [--report_consumables | --no-report_consumables] [--report_components | --no-report_components]
                           [--report_user_assets | --no-report_user_assets]

SnipeIT exporter for Prometheus

options:
  -h, --help            show this help message and exit
  --apikey APIKEY       SnipeIT API Key
  --target TARGET       SnipeIT instance url https://develop.snipeitapp.com
  --port PORT           Port on which to expose metrics and web interfa (default=9877)
  --asset_statuses ASSET_STATUSES [ASSET_STATUSES ...]
                        List of asset status names REQUIRED
  --asset_categories ASSET_CATEGORIES [ASSET_CATEGORIES ...]
                        List of asset categories names REQUIRED
  --report_consumables, --no-report_consumables
                        Report all consumables (default: False)
  --report_components, --no-report_components
                        Report all components (default: False)
  --report_user_assets, --no-report_user_assets
                        Report user assets (default: False)
```

### Examples
Snipe-IT graciously hosts a development instance for testing at https://develop.snipeitapp.com. The examples below contain public API keys to test. NEVER share your Snipe-IT API keys like you see in the examples below.

**Example 1:** Run with minimal arguments (just asset counts)

```shell
python snipeit_exporter.py \
    --target 'https://develop.snipeitapp.com' \
    --port 9877 \
    --apikey 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZTU2MDc0MjVmYjM5YTEwYjFjNTZlZTAxMTBmZDk4ZjQ0ZjVjODMzYjcxZWVhYjZlNDk1NGMwOThlY2YzMzU2MDY4Mzg4MmFhMDMzOTAzNzciLCJpYXQiOjE2MzI4NjU5MTgsIm5iZiI6MTYzMjg2NTkxOCwiZXhwIjoyMjY0MDIxNTE4LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.LgGVzyH67IRhXvccHd4j2Dn6TDuIuQTBoo30_wD9jPehy8v_h0xBmE1-dOUBRJyeJOI8B4gwPeALsWaudpGj9Lb5qWAtKV7eYtH9IYQKoLF_iHgOGXnAUcNwID6zBU_YyLNSI6gp8zjutLJias33CBLsHy5ZRNpxVibVrZouJ_HjYuIYbtZyLus-KFFeibtZoPiTWOeHhQFD37MR6ifx4dBqT37fN-xDS99mONtrkAplEIou5aSO1oZ4IlJIPCUyA1lixPgpn1YU7PxiBDZp1teeugD0WEmrAqxRS2I0bH4qPsuTsrVXS_lo87Sf5LBGLW7lGHKqyYH6J47OZOM0K-SrxLKtE1ww8jyLBgnnxH0lJHRLCBiwUnL5ZGTUmiOysUA-wSJ6s78o8Pc-ec6bpBvAlelHdiQ-wslE7gzEJDptbejFg-75b_CEwgJYh7J2D18ul6Qu5EFCUEgt033mm04dgVk0isWTDt6EW5ZvTo5Qhr1LY0YnEIXCTqIRN-BSQjL55sZaCrtwR_21bnBGgniyI5MRDYblFawVmFKroeClCpSjBo9vi66akdD5hjpvx67RL3r33BZQhEXmPifUPNH5wP_U-IHGFUD99TJk2c1awF0RASveZRLSunbJb1x6hGAVUaIvQV4r2quWzXqYyKLph9kGTyJYrb6iJtH5smE' \
    --asset_categories 'Laptops' \
    --asset_statuses 'Ready to Deploy' 'Pending' 
```

**Example 2:** Run with all arguments (asset counts, user assets counts, component & consumables remaining quantity)

```shell
python snipeit_exporter.py \
    --target 'https://develop.snipeitapp.com' \
    --port 9877 \
    --apikey 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZTU2MDc0MjVmYjM5YTEwYjFjNTZlZTAxMTBmZDk4ZjQ0ZjVjODMzYjcxZWVhYjZlNDk1NGMwOThlY2YzMzU2MDY4Mzg4MmFhMDMzOTAzNzciLCJpYXQiOjE2MzI4NjU5MTgsIm5iZiI6MTYzMjg2NTkxOCwiZXhwIjoyMjY0MDIxNTE4LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.LgGVzyH67IRhXvccHd4j2Dn6TDuIuQTBoo30_wD9jPehy8v_h0xBmE1-dOUBRJyeJOI8B4gwPeALsWaudpGj9Lb5qWAtKV7eYtH9IYQKoLF_iHgOGXnAUcNwID6zBU_YyLNSI6gp8zjutLJias33CBLsHy5ZRNpxVibVrZouJ_HjYuIYbtZyLus-KFFeibtZoPiTWOeHhQFD37MR6ifx4dBqT37fN-xDS99mONtrkAplEIou5aSO1oZ4IlJIPCUyA1lixPgpn1YU7PxiBDZp1teeugD0WEmrAqxRS2I0bH4qPsuTsrVXS_lo87Sf5LBGLW7lGHKqyYH6J47OZOM0K-SrxLKtE1ww8jyLBgnnxH0lJHRLCBiwUnL5ZGTUmiOysUA-wSJ6s78o8Pc-ec6bpBvAlelHdiQ-wslE7gzEJDptbejFg-75b_CEwgJYh7J2D18ul6Qu5EFCUEgt033mm04dgVk0isWTDt6EW5ZvTo5Qhr1LY0YnEIXCTqIRN-BSQjL55sZaCrtwR_21bnBGgniyI5MRDYblFawVmFKroeClCpSjBo9vi66akdD5hjpvx67RL3r33BZQhEXmPifUPNH5wP_U-IHGFUD99TJk2c1awF0RASveZRLSunbJb1x6hGAVUaIvQV4r2quWzXqYyKLph9kGTyJYrb6iJtH5smE' \
    --asset_categories 'Laptops' \
    --asset_statuses 'Ready to Deploy' 'Pending'  \
    --report_consumables \
    --report_components \
    --report_user_assets
```

## Requirements
This exporter has been tested on the following versions: `v6.1.2`

### API Tokens
The exporter requires a SnipeIT user with correct permission and API token see [Snipe-IT Generating API Tokens](https://snipe-it.readme.io/reference/generating-api-tokens)

### API Throttling
You may need to increase the default API throttling rate of 120 requests per minute by changing the API_THROTTLE_PER_MINUTE in .env on your target snipeIT instance to something like `API_THROTTLE_PER_MINUTE=300`. This will depend on how many assets you are pulling see [Snipe-IT API Throttling](https://snipe-it.readme.io/reference/api-throttling)

### Performance Tuning
Initial development was done on self hosted AWS instance with RDS database backend with around 3000+ assets. We found the following helps improve pooling times and overall performance.

* Limit status names. The more statuses to filter the longer polling time.
* Limit assets category names to only required assets for polling. 
* Increase Prometheus polling interval to at least 1 min to limit load on database. 
* Avoid additional latency on API calls by running exporter locally on the Snipe-IT instance.

## Installation
While not required it's recommended to run this exporter in a python virtual environment. The examples and install steps below do not cover this.

```
git clone https://github.com/gcet-net/snipeit-exporter
cd snipeit-exporter
pip install -r requirements.txt
```

## Additional Resources

* [Snipe-IT Development/Demo Instance](https://develop.snipeitapp.com)
* [Snipe-IT API Overview](https://snipe-it.readme.io/reference/api-overview)
* [Snipe-IT Swagger/OpenAPI Specification](https://snipe-it.readme.io/openapi/)
