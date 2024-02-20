import io
import json

import pandas as pd
import requests
from dagster import ConfigurableResource


class CovalentAPIResource(ConfigurableResource):
    """
    Covalent API instance
    """

    API_KEY: str

    def fetch_tx_page_for_address(self, chain_name: str, address: str, page: int):
        root = f"https://api.covalenthq.com/v1/{chain_name}/address/{address}/transactions_v3/page/{str(page)}/"
        response = requests.get(root, auth=(self.API_KEY, ""))
        response.raise_for_status()
        return response.json()

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


class DuneResource(ConfigurableResource):
    """
    Dune API resource.
    """

    DUNE_API_KEY: str

    def upload_csv(self, df: pd.DataFrame, name: str) -> requests.Response:
        """Uploads a CSV file to Dune's API.

        Args:
            csv_file_path (str): The path to the CSV file to upload.
        """

        url = "https://api.dune.com/api/v1/table/upload/csv"

        file_buffer = io.StringIO()
        df.to_csv(file_buffer, index=False)
        file_buffer.seek(0)
        df_csv = file_buffer.getvalue()

        headers = {"X-Dune-Api-Key": self.DUNE_API_KEY}
        payload = {
            "table_name": name,
            "is_private": False,
            "data": df_csv,
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        return response


class GrantsStackIndexerGraphQL(ConfigurableResource):
    ENDPOINT: str = "https://grants-stack-indexer-v2.gitcoin.co/graphql"

    def query(self, query: str, variables: dict = {}):
        response = requests.post(
            self.ENDPOINT,
            json={"query": query, "variables": variables},
        )
        response.raise_for_status()
        return response.json()
