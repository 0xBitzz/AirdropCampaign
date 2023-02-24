import os
import shutil
from typing import Final
from pyteal import (
    And,
    Seq,
    InnerTxnBuilder,
    TealType,
    TxnField,
    TxnType,
    Global,
    InnerTxn,
    Assert,
    AssetHolding
)
from beaker import Application, ApplicationStateValue, Authorize
from beaker.decorators import create, external
from pyteal.ast import abi, Int


class Asset(Application):
    asset: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        default=Int(0)
    )

    @create(authorize=Authorize.only(Global.creator_address()))
    def create(self):
        return self.initialize_application_state()

    @external(authorize=Authorize.only(Global.creator_address()))
    def create_asset(
            self,
            asset_name: abi.String,
            unit_name: abi.String,
            total_supply: abi.Uint64,
            *,
            output: abi.Uint64
    ):
        return Seq(
            Assert(self.asset == Int(0)),
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_name: asset_name.get(),
                TxnField.config_asset_unit_name: unit_name.get(),
                TxnField.config_asset_total: total_supply.get(),
                TxnField.config_asset_manager: Global.creator_address(),
                TxnField.fee: Int(1000)
            }),
            self.asset.set(InnerTxn.created_asset_id()),
            output.set(self.asset)
        )

    @external
    def opt_in_asset(
            self,
            txn: abi.AssetTransferTransaction,
            _asset: abi.Asset = asset  # type: ignore[assignment]
    ):
        return Seq(
            Assert(
                And(
                    txn.get().asset_amount() == Int(0),
                    txn.get().xfer_asset() == self.asset
                )
            )
        )

    @external(authorize=Authorize.only(Global.creator_address()))
    def transfer_asset(
            self,
            amount: abi.Uint64,
            receiver: abi.Account,  # type: ignore[assignment]
            _asset: abi.Asset = asset  # type: ignore[assignment]
    ):
        return Seq(
            InnerTxnBuilder.Execute({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: self.asset,
                TxnField.asset_receiver: receiver.address(),
                TxnField.asset_amount: amount.get(),
                TxnField.fee: Int(1000)
            }),
        )

    @external(read_only=True)
    def get_balance(
            self,
            account: abi.Account,  # type: ignore[assignment]
            _asset: abi.Asset = asset,  # type: ignore[assignment]
            *,
            output: abi.Uint64
    ):
        return Seq(
            (bal := AssetHolding.balance(account.address(), self.asset)),
            output.set(bal.value())
        )


if __name__ == "__main__":
    path = "./build"
    if os.path.exists(path):
        shutil.rmtree(path)
    Asset().dump(path)
