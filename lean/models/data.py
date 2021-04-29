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
from typing import Any, Dict, List, Optional

from pydantic import validator

from lean.models.api import QCResolution, QCSecurityType
from lean.models.pydantic import WrappedBaseModel


class DataFile(WrappedBaseModel):
    path: str
    security_type: QCSecurityType
    ticker: str
    market: str
    resolution: QCResolution
    date: Optional[datetime]

    def get_url(self) -> str:
        """Returns the link to the data in QuantConnect's Data Library."""
        if self.resolution == QCResolution.Daily or self.resolution == QCResolution.Hour:
            return f"https://www.quantconnect.com/data/file/{self.path}/{self.ticker.lower()}.csv"
        else:
            type = self.security_type.value.lower()
            resolution = self.resolution.value.lower()
            return f"https://www.quantconnect.com/data/tree/{type}/{self.market}/{resolution}/{self.ticker.lower()}"


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

        :return: the name of the security type in the data tree on QuantConnect.com
        """
        return {
            SecurityType.CFD: "cfd",
            SecurityType.Crypto: "crypto",
            SecurityType.Equity: "equity",
            SecurityType.EquityOption: "option",
            SecurityType.Forex: "forex",
            SecurityType.Future: "future",
            SecurityType.FutureOption: "futureoption",
            SecurityType.Index: "index",
            SecurityType.IndexOption: "indexoption"
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
    price: Optional[float] = None  # Price in USD
    purchased: Optional[bool] = None  # Whether the product is already purchased


class SecurityDataProduct(Product):
    security_type: SecurityType
    market: str
    resolution: QCResolution
    ticker: str
    start_date: Optional[datetime]  # Inclusive start date
    end_date: Optional[datetime]  # Inclusive end date
