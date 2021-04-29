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
from pathlib import Path
from typing import List

import click
import requests
from dateutil.rrule import DAILY, rrule, rruleset, weekday

from lean.components.api.api_client import APIClient
from lean.components.config.lean_config_manager import LeanConfigManager
from lean.components.util.logger import Logger
from lean.components.util.market_hours_database import MarketHoursDatabase
from lean.models.api import QCResolution
from lean.models.data import DataType, Product, SecurityDataProduct, SecurityType


class DataDownloader:
    """The DataDownloader is responsible for downloading data from the QuantConnect Data Library."""

    def __init__(self,
                 logger: Logger,
                 api_client: APIClient,
                 lean_config_manager: LeanConfigManager,
                 market_hours_database: MarketHoursDatabase):
        """Creates a new CloudBacktestRunner instance.

        :param logger: the logger to use to log messages with
        :param api_client: the APIClient instance to use when communicating with the QuantConnect API
        :param lean_config_manager: the LeanConfigManager instance to retrieve the data directory from
        :param market_hours_database: the MarketHoursDatabase instance to retrieve tradable days from
        """
        self._logger = logger
        self._api_client = api_client
        self._lean_config_manager = lean_config_manager
        self._market_hours_database = market_hours_database
        self._force_overwrite = None

    def download_products(self, products: List[Product], overwrite_flag: bool) -> None:
        """Downloads a list of products.

        :param products: the products to download
        :param overwrite_flag: whether the user has given permission to overwrite existing files
        """
        for index, product in enumerate(products):
            if isinstance(product, SecurityDataProduct):
                self.download_security_data(product, overwrite_flag, index + 1, len(products))
            elif product.data_type == DataType.MapFactor:
                self.download_map_factor(overwrite_flag, index + 1, len(products))
            elif product.data_type == DataType.Coarse:
                self.download_coarse(overwrite_flag, index + 1, len(products))

    def download_security_data(self,
                               product: SecurityDataProduct,
                               overwrite_flag: bool,
                               current_index: int,
                               total_products: int) -> None:
        """Downloads data of a specific security.

        :param product: the product to download
        :param overwrite_flag: whether the user has given permission to overwrite existing files
        :param current_index: the current index of the product in the list of products
        :param total_products: the total number of products that we're downloading
        """
        if product.resolution == QCResolution.Hour or product.resolution == QCResolution.Daily:
            dates = [None]
        else:
            dates = self._get_dates_with_data(product)

        files = []
        for date in dates:
            if product.security_type == SecurityType.FutureOption:
                for expiry_date in product.expiry_dates_by_data_date.get(date, []):
                    files.append(product.get_relative_path(date, expiry_date))
            else:
                files.append(product.get_relative_path(date, None))

        self._download_files(files, overwrite_flag, current_index, total_products)

    def download_map_factor(self, overwrite_flag: bool, current_index: int, total_products: int) -> None:
        """Downloads map and factor files.

        :param overwrite_flag: whether the user has given permission to overwrite existing files
        :param current_index: the current index of the product in the list of products
        :param total_products: the total number of products that we're downloading
        """
        # TODO: Download map/factor files using new API
        self._logger.info(f"[{current_index}/{total_products}] Downloading map and factor files")

    def download_coarse(self, overwrite_flag: bool, current_index: int, total_products: int) -> None:
        """Downloads coarse universe data.

        :param overwrite_flag: whether the user has given permission to overwrite existing files
        :param current_index: the current index of the product in the list of products
        :param total_products: the total number of products that we're downloading
        """
        # TODO: Download coarse universe data using new API
        self._logger.info(f"[{current_index}/{total_products}] Downloading coarse universe data")

    def _download_files(self, files: List[Path], overwrite_flag: bool, current_index: int, total_products: int) -> None:
        """Downloads files from the QuantConnect Data Library to the local data directory.

        The user should have already added the requested files to its QuantConnect account.

        :param files: the list of relative paths to download
        :param overwrite_flag: whether the user has given permission to overwrite existing files
        :param current_index: the current index of the product in the list of products
        :param total_products: the total number of products that we're downloading
        """
        data_dir = self._lean_config_manager.get_data_directory()

        for index, file in enumerate(files):
            self._logger.info(
                f"[{current_index}/{total_products}] [{index + 1}/{len(files)}] Downloading {file.as_posix()}")
            self._download_file(file, overwrite_flag, data_dir)

    def _download_file(self, relative_file: Path, overwrite_flag: bool, data_directory: Path) -> None:
        """Downloads a single file from the QuantConnect Data Library to the local data directory.

        :param relative_file: the relative path to the file in the data directory
        :param overwrite_flag: whether the user has given permission to overwrite existing files
        :param data_directory: the path to the local data directory
        """
        local_path = data_directory / relative_file

        if local_path.exists() and not self._should_overwrite(overwrite_flag, local_path):
            return

        # TODO: Download file using new API
        return

        link = self._api_client.data.get_link(relative_file.as_posix())
        link = link.link

        local_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(link)
        response.raise_for_status()

        if response.headers["content-type"] == "application/json":
            response_data = response.json()
            if "message" in response_data and "Not found" in response_data["message"]:
                self._logger.warn(f"{file.path} does not exist in the QuantConnect Data Library")
                return

        with local_path.open("wb+") as f:
            f.write(response.content)

    def _get_dates_with_data(self, product: SecurityDataProduct) -> List[datetime]:
        """Returns the dates between two dates for which the QuantConnect Data Library has data.

        The QuantConnect Data Library has data for all tradable days.
        This method uses the market hours database to find the tradable weekdays and the holidays.

        :param product: the product containing the information of the security data
        :return: the dates for which there is data for the given product
        """
        entry = self._market_hours_database.get_entry(product.security_type, product.market, product.ticker)

        # Create the set of rules containing all date rules
        rules = rruleset()

        # There is data on all weekdays on which the security trades
        weekdays_with_data = []
        for index, day in enumerate(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
            if len(getattr(entry, day)) > 0:
                weekdays_with_data.append(weekday(index))
        rules.rrule(rrule(DAILY, dtstart=product.start_date, until=product.end_date, byweekday=weekdays_with_data))

        # There is no data for holidays
        for holiday in entry.holidays:
            rules.exdate(holiday)

        # Return the dates of all tradable weekdays between the start and end date excluding the holidays
        return rules.between(product.start_date, product.end_date, inc=True)

    def _should_overwrite(self, overwrite_flag: bool, path: Path) -> bool:
        """Returns whether we should overwrite existing files.

        :param overwrite_flag: whether the user has given permission to overwrite existing files
        :param path: the path to the file that already exists
        :return: True if existing files may be overwritten, False if not
        """
        if overwrite_flag or self._force_overwrite:
            return True

        self._logger.warn(f"{path} already exists, use --overwrite to overwrite it")

        if self._force_overwrite is None:
            self._force_overwrite = click.confirm(
                "Do you want to temporarily enable overwriting for the previously selected products?",
                default=False)

        return self._force_overwrite
