"""
# SnipeIT Prometheus Exporter
"""
import time
import requests
import argparse
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class AppMetrics:
    """
    ## Prometheus Metrics
    """
    def __init__(self, args):
        self.apikey = args.apikey
        self.baseurl = args.target
        self.asset_status_names = args.asset_statuses
        self.asset_category_names = args.asset_categories
        self.report_consumables = args.report_consumables
        self.report_components = args.report_components
        self.report_user_assets = args.report_user_assets

    def get_metrics(self):
        """
        ### Call SnipeIT API to pull metrics
        See https://snipe-it.readme.io/reference/api-overview
        """
        baseurl = self.baseurl
        apikey = self.apikey
        headers = {
            "accept" : "application/json",
            "Authorization": f"Bearer {apikey}"
        }
        metrics = {
            "status": [],
            "model" : [],
            "hardware": [],
            "categories": [],
            "consumables": [],
            "components": [],
            "user_asset": []
        }

        # Get status ids
        asset_status_names = self.asset_status_names
        status_endpoint = f"{baseurl}/api/v1/statuslabels"
        r_status = requests.get(status_endpoint, headers=headers)

        # Raise bad requests
        r_status.raise_for_status()

        for m in r_status.json()['rows']:
            if m.get('name') in asset_status_names:
                metrics['status'].append({
                    "name": f"{m.get('name')}",
                    "id": m.get('id'),
                    "count": m.get('assets_count')
                })

        # Get categories
        asset_category_names = self.asset_category_names
        r_categories = requests.get(
            f"{baseurl}/api/v1/categories?limit=1000",
            headers=headers
        )
        for category in r_categories.json()['rows']:
            if category.get('name') in asset_category_names:
                metrics['categories'].append({
                    "name": f"{category.get('name')}",
                    "id": category.get('id')
                })

        # Get asset model counts by group
        for category in metrics.get('categories'):
            model_endpoint = f"{baseurl}/api/v1/models?limit=1000&category_id={category.get('id')}"
            r_model = requests.get(model_endpoint, headers=headers)
            for model in r_model.json()['rows']:
                for status in metrics.get('status'):
                    # Nasty loop has to be a better way to get status of hardware
                    # This will not work pulling all assets
                    hardware_endpoint = (
                        f"{baseurl}/api/v1/hardware?limit=1&offset=0"
                        f"&status_id={status.get('id')}&model_id={model.get('id')}"
                    )
                    hardware = requests.get(hardware_endpoint, headers=headers).json()
                    metrics['hardware'].append({
                        "name": f"{model.get('name')}",
                        "model_number": f"{model.get('model_number')}",
                        "status": f"{status.get('name')}",
                        "count": hardware.get('total')
                    })

        # Get consumables
        if self.report_consumables:
            r_consumables = requests.get(
                f"{baseurl}/api/v1/consumables?limit=1000",
                headers=headers
            )
            for consumable in r_consumables.json()['rows']:
                metrics['consumables'].append({
                    "name": f"{consumable.get('name')}",
                    "model_number": f"{consumable.get('model_number')}",
                    "min_amt": consumable.get('min_amt'),
                    "remaining": consumable.get('remaining'),
                    "qty": consumable.get('qty'),
                })

        # Get components
        if self.report_components:
            r_components = requests.get(
                f"{baseurl}/api/v1/components?limit=1000",
                headers=headers
            )
            for component in r_components.json()['rows']:
                metrics['components'].append({
                    "name": f"{component.get('name')}",
                    "serial": f"{component.get('serial')}",
                    "min_amt": component.get('min_amt'),
                    "remaining": component.get('remaining'),
                    "qty": component.get('qty'),
                })

        # Get user asset counts
        if self.report_user_assets:
            r_user = requests.get(f"{baseurl}/api/v1/users?limit=1000", headers=headers)
            for user in r_user.json()['rows']:
                # Get user asset counts
                asset_counts = {}
                asset_names = {}
                asset_model_numbers = []
                for asset in metrics['hardware']:
                    asset_model_numbers.append(asset.get('model_number'))
                    asset_counts.update({asset.get('model_number'): 0})
                    asset_names.update({asset.get('model_number'): asset.get('name')})

                # Get user asset counts
                r_user_asset = requests.get(f"{baseurl}/api/v1/users/{user.get('id')}/assets", headers=headers)
                for asset in r_user_asset.json()['rows']:
                    if (asset.get('model_number') in asset_model_numbers):
                        asset_counts[asset.get('model_number')]+=1

                for asset in asset_counts:
                    if asset_counts[asset] > 0:
                        metrics['user_asset'].append({
                            "user": f"{user.get('username')}",
                            "model_name": f"{asset_names[asset]}",
                            "model_number": f"{asset}",
                            "count": asset_counts[asset]
                        })
        return metrics

    def collect(self):
        """
        ### Collect Prometheus metrics
        """
        metrics = self.get_metrics()
        asset_metrics = {
            'asset': GaugeMetricFamily(
                'snipeit_asset_count',
                'SnipeIt Assets',
                labels=['name', 'model_number', 'status']
            )
        }
        consumable_metrics = {
            'consumable': GaugeMetricFamily(
                'snipeit_consumable_remaining',
                'SnipeIt remaining consumable quantity',
                labels=['name', 'model_number']
            )
        }
        component_metrics = {
            'component': GaugeMetricFamily(
                'snipeit_component_remaining',
                'SnipeIt remaining component quantity',
                labels=['name', 'serial']
            )
        }
        user_asset_metrics = {
            'user_asset': GaugeMetricFamily(
                'snipeit_asset_count_user',
                'SnipeIt user asset counts',
                labels=['user', 'name', 'model_number']
            )
        }

        # Asset
        for asset in metrics['hardware']:
            asset_metrics['asset'].add_metric(
                [asset.get('name'), asset.get('model_number'), asset.get('status')],
                asset.get('count')
            )
        for m in asset_metrics.values():
            yield m

        # User Assets
        for user in metrics['user_asset']:
            user_asset_metrics['user_asset'].add_metric(
                [user.get('user'), user.get('model_name'), user.get('model_number')],
                user.get('count')
            )
        for m in user_asset_metrics.values():
            yield m

        # Consumable
        for consumable in metrics['consumables']:
            consumable_metrics['consumable'].add_metric(
                [consumable.get('name'), consumable.get('model_number')],
                consumable.get('remaining')
            )
        for m in consumable_metrics.values():
            yield m

        # Component
        for component in metrics['components']:
            component_metrics['component'].add_metric(
                [component.get('name'), component.get('serial')],
                component.get('remaining')
            )
        for m in component_metrics.values():
            yield m

def parse_args():
    """
    ## Command-line parsing arguments
    """
    parser = argparse.ArgumentParser(description='SnipeIT exporter for Prometheus')
    parser.add_argument('--apikey', type=str, required=True,
                        help='SnipeIT API Key')
    parser.add_argument('--target', type=str, required=True,
                        help='SnipeIT instance url https://develop.snipeitapp.com')
    parser.add_argument('--port', type=int, default=9877,
                        help='Port on which to expose metrics and web interface (default=9877)')
    parser.add_argument('--asset_statuses', nargs='+', default=['Ready to Deploy', 'Pending'],
                        help='List of asset status names REQUIRED')
    parser.add_argument('--asset_categories', nargs='+', default=['Laptops', 'Desktops'],
                        help='List of asset categories names REQUIRED')
    parser.add_argument('--report_consumables', default=False, action=argparse.BooleanOptionalAction,
                        help='Report all consumables')
    parser.add_argument('--report_components', default=False, action=argparse.BooleanOptionalAction,
                        help='Report all components')
    parser.add_argument('--report_user_assets', default=False, action=argparse.BooleanOptionalAction,
                         help='Report user assets')
    return parser.parse_args()

def main():
    args = parse_args()

    start_http_server(int(args.port))
    REGISTRY.register(AppMetrics(args))

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
