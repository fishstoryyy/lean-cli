# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from random import randint
from typing import List

import click
from rich import box
from rich.table import Table

from lean.click import DateParameter, LeanCommand
from lean.container import container
from lean.models.api import QCResolution
from lean.models.data import DataType, OptionStyle, Product, SecurityDataProduct, SecurityType
from lean.models.errors import MoreInfoError
from lean.models.logger import Option

_future_option_to_future = {
    "OEH": "EH",
    "OKE": "KE",
    "OTN": "TN",
    "OUB": "UB",
    "OYM": "YM",
    "OZB": "ZB",
    "OZC": "ZC",
    "OZF": "ZF",
    "OZL": "ZL",
    "OZM": "ZM",
    "OZN": "ZN",
    "OZO": "ZO",
    "OZS": "ZS",
    "OZT": "ZT",
    "OZW": "ZW",
    "RTO": "RTY",
    "OG": "GC",
    "HXE": "HG",
    "SO": "SI",
    "LO": "CL",
    "HCO": "HCL",
    "OH": "HO",
    "ON": "NG",
    "PAO": "PA",
    "PO": "PL",
    "OB": "RB"
}


def _display_products(products: List[Product]) -> None:
    """Previews a list of products in pretty tables.

    Uses the API to get the latest price information.

    :param products: the products to display
    """
    # TODO: Get price and date range information from new API
    for product in products:
        if product.price is None:
            product.price = randint(10, 10000)
            product.purchased = randint(0, 100) < 10

        if isinstance(product, SecurityDataProduct):
            if product.start_date is None:
                product.start_date = datetime(2000, 1, 1)
                product.end_date = datetime.now()

            if product.security_type == SecurityType.FutureOption and product.expiry_dates_by_data_date is None:
                product.expiry_dates_by_data_date = {}

    security_data_products = [p for p in products if isinstance(p, SecurityDataProduct)]
    subscription_products = [p for p in products if not isinstance(p, SecurityDataProduct)]

    logger = container.logger()

    if len(security_data_products) > 0:
        table = Table(box=box.SQUARE)

        for column in ["Ticker", "Security type", "Data type", "Date range", "Market", "Resolution", "Price"]:
            table.add_column(column)

        for product in security_data_products:
            table.add_row(product.ticker.upper(),
                          product.security_type.value,
                          product.data_type.value,
                          f"{product.start_date.strftime('%Y-%m-%d')} - {product.end_date.strftime('%Y-%m-%d')}",
                          product.market,
                          product.resolution.value,
                          f"${product.price:,.2f}{'*' if product.purchased else ''}")

        logger.info(table)

        if any([p.purchased for p in security_data_products]):
            logger.info("* = product already purchased")

    if len(subscription_products) > 0:
        table = Table(box=box.SQUARE)

        for column in ["Subscription", "Price per year"]:
            table.add_column(column)

        for product in subscription_products:
            table.add_row(product.data_type.value,
                          f"${product.price:,.2f}{'*' if product.purchased else ''}")

        logger.info(table)

        if any([p.purchased for p in subscription_products]):
            logger.info("* = product already subscribed to")

    now_price_usd = sum([p.price for p in products if not p.purchased])
    now_price_qcc = now_price_usd * 100

    yearly_price_usd = sum([p.price for p in products if not isinstance(p, SecurityDataProduct)])
    yearly_price_qcc = yearly_price_usd * 100

    logger.info(f"Total price due now: ${now_price_usd:,.2f} ({now_price_qcc:,.2f} QCC)")
    logger.info(f"Yearly subscriptions: ${yearly_price_usd:,.2f} / year ({yearly_price_qcc:,.2f} QCC / year)")


def _select_products() -> List[Product]:
    """Asks the user for the products that should be purchased and downloaded.

    :return: the list of products selected by the user
    """
    products = []
    logger = container.logger()

    while True:
        security_type = logger.prompt_list("Select the security type of the data", [
            Option(value=s, label=s.value) for s in SecurityType.__members__.values()
        ])

        # It is impossible to have 2 subscriptions of the same type at the same time
        data_types_to_skip = {p.data_type for p in products if p.data_type.is_subscription()}

        available_data_types = security_type.get_data_types()
        data_type = logger.prompt_list("Select the data type", [
            Option(value=t, label=t.value) for t in [x for x in available_data_types if x not in data_types_to_skip]
        ])

        if data_type == DataType.Trade or data_type == DataType.Quote or data_type == DataType.OpenInterest:
            market = logger.prompt_list("Select the market of the data", [
                Option(value=m, label=m) for m in security_type.get_markets()
            ])

            resolution = logger.prompt_list("Select the resolution of the data", [
                Option(value=r, label=r.value) for r in security_type.get_resolutions(data_type)
            ])

            logger.info(
                f"Browse the available data at https://www.quantconnect.com/data/tree/{security_type.get_internal_name().lower()}/{market.lower()}/{resolution.value.lower()}")
            ticker = click.prompt("Enter the ticker of the data")

            if security_type in [SecurityType.EquityOption, SecurityType.FutureOption, SecurityType.IndexOption]:
                option_style = logger.prompt_list("Select the option style of the data", [
                    Option(value=s, label=s.value) for s in OptionStyle.__members__.values()
                ])
            else:
                option_style = None

            if resolution != QCResolution.Hour and resolution != QCResolution.Daily:
                start_date = click.prompt("Start date of the data (yyyyMMdd, leave empty to select all available data)",
                                          type=DateParameter(),
                                          default=False,
                                          show_default=False)

                if start_date:
                    while True:
                        end_date = click.prompt("End date of the data (yyyyMMdd)", type=DateParameter())
                        if end_date <= start_date:
                            logger.info("Error: end date must be later than start date")
                        else:
                            break
                else:
                    start_date = None
                    end_date = None
            else:
                start_date = None
                end_date = None

            products.append(SecurityDataProduct(security_type=security_type,
                                                data_type=data_type,
                                                market=market,
                                                resolution=resolution,
                                                ticker=ticker,
                                                start_date=start_date,
                                                end_date=end_date,
                                                option_style=option_style,
                                                expiry_dates_by_data_date=None))

            # Future option data without the data of the underlying future isn't very useful
            if security_type == SecurityType.FutureOption:
                underlying_future = _future_option_to_future.get(ticker.upper(), None)

                underlying_known = underlying_future is not None
                underlying_added = any(p.security_type == SecurityType.Future
                                       and p.data_type == data_type
                                       and p.ticker == underlying_future for p in products)

                if underlying_known and not underlying_added:
                    logger.info("The underlying Futures data is required to use Future Options data.")
                    logger.info("Without it, you will not be able to run a Future Option backtest.")
                    logger.info(
                        "If you have your own Futures data we cannot guarantee your local backtests will match the cloud backtests.")
                    if click.confirm("Would you like to add the underlying asset data as well?", default=True):
                        products.append(SecurityDataProduct(security_type=SecurityType.Future,
                                                            data_type=data_type,
                                                            market=market,
                                                            resolution=resolution,
                                                            ticker=underlying_future,
                                                            start_date=start_date,
                                                            end_date=end_date,
                                                            option_style=None,
                                                            expiry_dates_by_data_date=None))

            # Equity data requires a map and factor files subscription
            if security_type == SecurityType.Equity and not any([p.data_type == DataType.MapFactor for p in products]):
                logger.info("Automatically adding a subscription for map and factor files (required for equity data)")
                products.append(Product(data_type=DataType.MapFactor))
        else:
            products.append(Product(data_type=data_type))

        logger.info("Selected products:")
        _display_products(products)

        if not click.confirm("Do you want to add another product?"):
            break

    return products


def _confirm_distribution_agreements(products: List[Product]) -> None:
    """Asks the user to agree to the required distribution agreements.

    An abort error is raised if the user doesn't agree to an agreement.

    :param products: the list of products selected by the user
    """
    logger = container.logger()

    # TODO: Get required agreements from new API
    logger.info("TODO: Get required agreements from new API")

    data_providers = ["Oanda", "GDAX"]

    if len(data_providers) > 0:
        logger.info("You need to accept the terms and conditions of each data provider you're downloading data from")

    for provider in data_providers:
        logger.info(
            f"Terms and conditions for {provider}: https://www.quantconnect.com/data/provider/{provider.lower()}")
        click.confirm(f"Do you accept the terms and conditions for {provider}?", abort=True)


def _process_payment(products: List[Product]) -> None:
    """Processes payment for the selected products.

    An abort error is raised if the user decides to cancel.

    :param products: the list of products selected by the user
    """
    price_usd = sum([p.price for p in products if not p.purchased])
    price_qcc = price_usd * 100

    primary_org = container.api_client().accounts.get_organization()

    if price_qcc > primary_org.creditBalance and primary_org.card is None:
        raise MoreInfoError("The total price exceeds your QCC balance, please add a credit card to your organization",
                            "https://www.quantconnect.com/terminal/#organization/billing")

    logger = container.logger()

    if price_qcc <= primary_org.creditBalance:
        logger.info(f"You will be billed {price_qcc:,.2f} QCC (${price_usd:,.2f}) from your organization's QCC balance")
    elif primary_org.creditBalance > 0:
        billed_qcc = primary_org.creditBalance
        billed_usd = price_usd - billed_qcc / 100

        logger.info(f"You will be billed ${price_usd:,.2f}, divided as follows:")
        logger.info(f"- {billed_qcc:,.2f} QCC (${billed_qcc / 100:,.2f}) from your organization's QCC balance")
        logger.info(f"- ${billed_usd:,.2f} from your organization's credit card ending in {primary_org.card.last4}")
    else:
        logger.info(
            f"You will be billed ${price_usd:,.2f} from your organization's credit card ending in {primary_org.card.last4}")

    click.confirm("Continue?", abort=True)

    # TODO: Process payment using new API
    logger.info("TODO: Process payment using new API")


@click.command(cls=LeanCommand, requires_lean_config=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing local data")
def download(overwrite: bool) -> None:
    """Purchase and download data from QuantConnect's Data Library.

    An interactive wizard will show to walk you through the process of selecting data,
    agreeing to the distribution agreements and payment. Certain steps will be skipped
    if you already purchased the selected data. After this wizard the selected data
    will be downloaded automatically.

    \b
    See the following url for the data that can be purchased and downloaded with this command:
    https://www.quantconnect.com/data/tree
    """
    products = _select_products()

    _confirm_distribution_agreements(products)
    _process_payment(products)

    container.data_downloader().download_products(products, overwrite)
