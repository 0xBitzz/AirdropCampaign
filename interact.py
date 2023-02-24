import os
import csv
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.error import AlgodHTTPError
from algosdk.logic import get_application_address
from beaker.client.api_providers import AlgoNode, Network
from beaker.client import ApplicationClient
from contract import Asset
from dotenv import load_dotenv

load_dotenv()

APP_ID = 52
ASSET_ID = 55

CREATOR = {
    "signer":  os.getenv("CREATOR_SK"),
    "address": os.getenv("CREATOR_ADDR")
}
ESCROW_ADDRESS = get_application_address(APP_ID)

FILE_PATH = "modules/account/eligible_addresses.csv"


class Airdrop:
    client = AlgoNode(Network.TestNet).algod()

    def __init__(self, addresses_file_path, creator_signer: AccountTransactionSigner):
        self.addresses_file_path = addresses_file_path
        self.creator_signer = creator_signer
        self.app_client = ApplicationClient(self.client, Asset(), APP_ID, signer=creator_signer)
        self.airdrop_to_accounts()

    def read_from_csv(self):
        addresses = []
        with open(self.addresses_file_path, "r", newline="") as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            print(header)
            for _row in csv_reader:
                addresses.append(_row)
        return addresses

    def airdrop_to_accounts(self):
        for row in self.read_from_csv():
            _, address, _, amount = "".join(row).split(",")
            try:
                amount = int(amount)
                self.app_client.call(Asset.transfer_asset, receiver=address, amount=amount, signer=self.creator_signer)
                print(self.client.account_asset_info(address, ASSET_ID))
            except AlgodHTTPError as e:
                print(e)


Airdrop(addresses_file_path=FILE_PATH, creator_signer=AccountTransactionSigner(CREATOR["signer"]))
