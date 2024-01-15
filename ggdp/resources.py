import requests
from dagster import ConfigurableResource


class CovalentAPIResource(ConfigurableResource):
    """
    Covalent API instance
    """

    API_KEY: str

    def fetch_tx_page_for_address(self, chain_name: str, address: str, page: int):
        root = f"https://api.covalenthq.com/v1/{chain_name}/address/{address}/transactions_v3/page/{str(page)}/"
        page = requests.get(root, auth=(self.API_KEY, ""))
        page.raise_for_status()
        return page.json()

    def fetch_all_tx_for_address(self, chain_name: str, address: str):
        output = []
        page = 1
        while True:
            current_page = self.fetch_tx_page_for_address(chain_name, address, page)
            if current_page is None:
                break
            output.append(current_page["data"])
            if not current_page["data"]["links"].get("next"):
                break
            page += 1
        return output
