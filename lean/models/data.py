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
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import validator

from lean.models.api import QCResolution
from lean.models.pydantic import WrappedBaseModel


class MarketHoursSegment(WrappedBaseModel):
    start: str
    end: str
    state: str


class MarketHoursDatabaseEntry(WrappedBaseModel):
    dataTimeZone: str
    exchangeTimeZone: str
    monday: List[MarketHoursSegment] = []
    tuesday: List[MarketHoursSegment] = []
    wednesday: List[MarketHoursSegment] = []
    thursday: List[MarketHoursSegment] = []
    friday: List[MarketHoursSegment] = []
    saturday: List[MarketHoursSegment] = []
    sunday: List[MarketHoursSegment] = []
    holidays: List[datetime] = []
    earlyCloses: Dict[str, str] = {}
    lateOpens: Dict[str, str] = {}

    @validator("holidays", pre=True)
    def parse_holidays(cls, value: Any) -> Any:
        if isinstance(value, list):
            return [datetime.strptime(x, "%m/%d/%Y") for x in value]
        return value


class DataType(str, Enum):
    Trade = "Trade data"
    Quote = "Quote data"
    OpenInterest = "Open interest data"

    MapFactor = "Map and factor files (yearly subscription)"
    Coarse = "Coarse universe data (yearly subscription)"

    def is_subscription(self) -> bool:
        """Returns whether the data type is a subscription or not.

        :return: True if the data type is a subscription, False if not
        """
        return self == DataType.MapFactor or self == DataType.Coarse


class SecurityType(str, Enum):
    CFD = "CFD"
    Crypto = "Crypto"
    Equity = "Equity"
    EquityOption = "Equity option"
    Forex = "Forex"
    Future = "Future"
    FutureOption = "Future option"
    Index = "Index"
    IndexOption = "Index option"

    def get_internal_name(self) -> str:
        """Returns the internal name of the security type.

        :return: the name of the security type in LEAN
        """
        return {
            SecurityType.CFD: "Cfd",
            SecurityType.Crypto: "Crypto",
            SecurityType.Equity: "Equity",
            SecurityType.EquityOption: "Option",
            SecurityType.Forex: "Forex",
            SecurityType.Future: "Future",
            SecurityType.FutureOption: "FutureOption",
            SecurityType.Index: "Index",
            SecurityType.IndexOption: "IndexOption"
        }[self]

    def get_data_types(self) -> List[DataType]:
        """Returns the available data types.

        :return: the data types for which there is data for sale
        """
        return {
            SecurityType.CFD: [DataType.Quote],
            SecurityType.Crypto: [DataType.Trade, DataType.Quote],
            SecurityType.Equity: [DataType.Trade, DataType.Quote, DataType.MapFactor, DataType.Coarse],
            SecurityType.EquityOption: [DataType.Trade, DataType.Quote, DataType.OpenInterest],
            SecurityType.Forex: [DataType.Quote],
            SecurityType.Future: [DataType.Trade, DataType.Quote, DataType.OpenInterest],
            SecurityType.FutureOption: [DataType.Trade, DataType.Quote, DataType.OpenInterest],
            SecurityType.Index: [DataType.Trade],
            SecurityType.IndexOption: [DataType.Trade, DataType.Quote, DataType.OpenInterest]
        }[self]

    def get_markets(self) -> List[str]:
        """Returns the available markets.

        :return: the markets for which there is data for sale
        """
        return {
            SecurityType.CFD: ["Oanda"],
            SecurityType.Crypto: ["Bitfinex", "GDAX"],
            SecurityType.Equity: ["USA"],
            SecurityType.EquityOption: ["USA"],
            SecurityType.Forex: ["FXCM", "Oanda"],
            SecurityType.Future: ["CBOE", "CBOT", "CME", "COMEX", "NYMEX"],
            SecurityType.FutureOption: ["CBOT", "CME", "COMEX", "NYMEX"],
            SecurityType.Index: ["USA"],
            SecurityType.IndexOption: ["USA"]
        }[self]

    def get_resolutions(self, data_type: DataType) -> List[QCResolution]:
        """Returns the available resolutions.

        :param data_type: the type of the requested data
        :return the resolutions for which there is data for sale
        """
        all_resolutions = [QCResolution.Tick,
                           QCResolution.Second,
                           QCResolution.Minute,
                           QCResolution.Hour,
                           QCResolution.Daily]

        return {
            SecurityType.CFD: all_resolutions,
            SecurityType.Crypto: all_resolutions,
            SecurityType.Equity: all_resolutions if data_type is DataType.Trade else [QCResolution.Tick,
                                                                                      QCResolution.Second,
                                                                                      QCResolution.Minute],
            SecurityType.EquityOption: [QCResolution.Minute],
            SecurityType.Forex: all_resolutions,
            SecurityType.Future: [QCResolution.Tick, QCResolution.Second, QCResolution.Minute],
            SecurityType.FutureOption: [QCResolution.Minute],
            SecurityType.Index: all_resolutions,
            SecurityType.IndexOption: [QCResolution.Minute]
        }[self]


class Product(WrappedBaseModel):
    data_type: DataType

    # Price in USD
    price: Optional[float] = None

    # Whether the product is already purchased
    purchased: Optional[bool] = None

    def get_data_files(self) -> List[str]:
        pass


class OptionStyle(str, Enum):
    American = "American"
    European = "European"


class SecurityDataProduct(Product):
    security_type: SecurityType
    market: str
    resolution: QCResolution
    ticker: str

    # Inclusive start date
    start_date: Optional[datetime]

    # Inclusive end date
    end_date: Optional[datetime]

    option_style: Optional[OptionStyle]

    # Date of data -> expiry dates of the available contracts
    expiry_dates_by_data_date: Optional[Dict[datetime, List[datetime]]]

    def get_relative_path(self, data_date: Optional[datetime], expiry_date: Optional[datetime]) -> Path:
        """Returns the relative path of the data file of a given date in the data directory.

        :param data_date: the date of the data to get the path to, ignored for hourly or daily data
        :param expiry_date: the expiry date of the option contracts, only used for future options data
        :return: the path to the file containing the data of the given data relative to the data directory
        """
        return self._get_relative_zip_file_directory(expiry_date) / self._get_zip_file_name(data_date)

    def _get_relative_zip_file_directory(self, expiry_date: Optional[datetime]) -> Path:
        """Returns the relative path of the directory containing the data file in the data directory.

        :param expiry_date: the expiry date of the option contracts, only used for future options data
        :return: the path to the directory containing the data files of this product relative to the data directory
        """
        type_name = self.security_type.get_internal_name().lower()
        base_directory = Path(type_name) / self.market.lower() / self.resolution.value.lower()

        if self.resolution == QCResolution.Hour or self.resolution == QCResolution.Daily:
            return base_directory

        if self.security_type in [SecurityType.CFD,
                                  SecurityType.Crypto,
                                  SecurityType.Equity,
                                  SecurityType.EquityOption,
                                  SecurityType.Forex,
                                  SecurityType.Future,
                                  SecurityType.Index,
                                  SecurityType.IndexOption]:
            return base_directory / self.ticker.lower()
        elif self.security_type == SecurityType.FutureOption:
            return base_directory / self.ticker.lower() / expiry_date.strftime("%Y%m%d")
        else:
            raise ValueError(f"Unknown security type: {self.security_type}")

    def _get_zip_file_name(self, data_date: Optional[datetime]) -> str:
        """Returns the name of data file containing the data for a given date.

        :param data_date: the date of the data to get the path to, ignored for hourly or daily data
        :return: the name of the zip file containing the data for the given date
        """
        tick_type = self.data_type.name.lower()
        formatted_date = data_date.strftime("%Y%m%d") if data_date is not None else None
        is_hour_or_daily = self.resolution == QCResolution.Hour or self.resolution == QCResolution.Daily

        if self.security_type in [SecurityType.CFD, SecurityType.Equity, SecurityType.Forex, SecurityType.Index]:
            if is_hour_or_daily:
                return f"{self.ticker.lower()}.zip"
            else:
                return f"{formatted_date}_{tick_type}.zip"
        elif self.security_type in [SecurityType.Crypto, SecurityType.Future]:
            if is_hour_or_daily:
                return f"{self.ticker.lower()}_{tick_type}.zip"
            else:
                return f"{formatted_date}_{tick_type}.zip"
        elif self.security_type in [SecurityType.EquityOption, SecurityType.IndexOption, SecurityType.FutureOption]:
            if is_hour_or_daily:
                return f"{self.ticker.lower()}_{tick_type}_{self.option_style.name.lower()}.zip"
            else:
                return f"{formatted_date}_{tick_type}_{self.option_style.name.lower()}.zip"
        else:
            raise ValueError(f"Unknown security type: {self.security_type}")
