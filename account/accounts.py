import csv
import os
import shutil
from algosdk import account

FILE_PATH = "eligible_addresses.csv"


def generate_accounts():
    accounts = []
    for i in range(10):
        sk, addr = account.generate_account()
        acct = {"addr": addr, "sk": sk}
        accounts.append(acct)
    return accounts


def write_accounts():
    if os.path.exists(FILE_PATH):
        shutil.rmtree(FILE_PATH)
    else:
        accounts = generate_accounts()
        with open(FILE_PATH, "w", newline="") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(["S/No.,Address,Sk,Amount"])
            for i in range(10):
                csv_writer.writerow([f"{i+1},{accounts[i]['addr']},{accounts[i]['sk']},{10}"])


write_accounts()


