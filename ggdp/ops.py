import io
import json
import os

import pandas as pd
import requests as rq
from dagster import OpExecutionContext, job, op

from .assets import raw_allo_deployments


@op()
def tiny_upload_to_dune(context: OpExecutionContext, data: pd.DataFrame) -> None:
    """
    Upload select dataframe to dune using API, needs DUNE_API_KEY envar to succeeed.
    """

    DUNE_KEY = os.getenv("DUNE_API_KEY")
    if DUNE_KEY is None:
        raise ValueError("DUNE_API_KEY envar not set, cannot upload")

    file_buffer = io.StringIO()
    data.to_csv(file_buffer, index=False)
    file_buffer.seek(0)
    csv_content = file_buffer.getvalue()

    upload_payload = json.dumps(
        {"table_name": "allo_contract_deployments", "data": csv_content}
    )

    response = rq.post(
        "https://api.dune.com/api/v1/table/upload/csv",
        headers={"X-Dune-Api-Key": DUNE_KEY},
        data=upload_payload,
    )
    context.log.info(
        f"new data uploaded to dune, result:{str(response.status_code)} | {str(response.text)}"
    )

    response.raise_for_status()


@job
def refresh_dune():
    """
    Refresh public dune dataset by materializing `raw_allo_deployments` and uploading new version.
    """
    tiny_upload_to_dune(data=raw_allo_deployments())
