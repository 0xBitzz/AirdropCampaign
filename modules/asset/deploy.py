import os
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from beaker.client.api_providers import Network, AlgoNode
from beaker.client import ApplicationClient
from beaker import consts
from dotenv import load_dotenv
from contract import Asset

load_dotenv()

CREATOR = {
    "signer": AccountTransactionSigner(os.getenv("CREATOR_SK")),
    "address": os.getenv("CREATOR_ADDR")
}


def deploy() -> None:
    client = AlgoNode(Network.TestNet).algod()
    app_client = ApplicationClient(client, Asset(), signer=CREATOR["signer"])

    app_id: int
    escrow_address: str
    app_id, escrow_address, _ = app_client.create()
    print(f"App ID: {app_id}")
    print(f"Escrow address: {escrow_address}")

    app_client.fund(consts.algo)

    asset_id: int = app_client.call(
        Asset.create_asset, asset_name="XYZ", unit_name="XYZ", total_supply=10000
    ).return_value
    print(f"Asset ID: {asset_id}")

    escrow_bal: int = app_client.call(Asset.get_balance, account=escrow_address).return_value
    print(f"Escrow balance of XYZ: {escrow_bal}")


deploy()
