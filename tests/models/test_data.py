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

from typing import List

import pytest

from lean.models.api import QCResolution
from lean.models.data import DataType, SecurityType


@pytest.mark.parametrize("data_type,result", [(DataType.Trade, False),
                                              (DataType.Quote, False),
                                              (DataType.OpenInterest, False),
                                              (DataType.MapFactor, True),
                                              (DataType.Coarse, True)])
def test_data_type_is_resolution_returns_whether_type_is_subscription(data_type: DataType, result: bool) -> None:
    assert data_type.is_subscription() == result


@pytest.mark.parametrize("security_type,result", [(SecurityType.CFD, "cfd"),
                                                  (SecurityType.Crypto, "crypto"),
                                                  (SecurityType.Equity, "equity"),
                                                  (SecurityType.EquityOption, "option"),
                                                  (SecurityType.Forex, "forex"),
                                                  (SecurityType.Future, "future"),
                                                  (SecurityType.FutureOption, "futureoption"),
                                                  (SecurityType.Index, "index"),
                                                  (SecurityType.IndexOption, "indexoption")])
def test_security_type_get_internal_name_returns_name_in_data_tree(security_type: SecurityType, result: str) -> None:
    assert security_type.get_internal_name() == result


@pytest.mark.parametrize("security_type,result", [
    (SecurityType.CFD, [DataType.Quote]),
    (SecurityType.Crypto, [DataType.Trade, DataType.Quote]),
    (SecurityType.Equity, [DataType.Trade, DataType.Quote, DataType.MapFactor, DataType.Coarse]),
    (SecurityType.EquityOption, [DataType.Trade, DataType.Quote, DataType.OpenInterest]),
    (SecurityType.Forex, [DataType.Quote]),
    (SecurityType.Future, [DataType.Trade, DataType.Quote, DataType.OpenInterest]),
    (SecurityType.FutureOption, [DataType.Trade, DataType.Quote, DataType.OpenInterest]),
    (SecurityType.Index, [DataType.Trade]),
    (SecurityType.IndexOption, [DataType.Trade, DataType.Quote, DataType.OpenInterest])
])
def test_security_type_get_data_types_returns_available_data_types(security_type: SecurityType,
                                                                   result: List[DataType]) -> None:
    assert sorted(security_type.get_data_types()) == sorted(result)


@pytest.mark.parametrize("security_type,result", [(SecurityType.CFD, ["Oanda"]),
                                                  (SecurityType.Crypto, ["Bitfinex", "GDAX"]),
                                                  (SecurityType.Equity, ["USA"]),
                                                  (SecurityType.EquityOption, ["USA"]),
                                                  (SecurityType.Forex, ["FXCM", "Oanda"]),
                                                  (SecurityType.Future, ["CBOE", "CBOT", "CME", "COMEX", "NYMEX"]),
                                                  (SecurityType.FutureOption, ["CBOT", "CME", "COMEX", "NYMEX"]),
                                                  (SecurityType.Index, ["USA"]),
                                                  (SecurityType.IndexOption, ["USA"])])
def test_security_type_get_markets_returns_available_markets(security_type: SecurityType, result: List[str]) -> None:
    assert sorted(security_type.get_markets()) == sorted(result)


all_resolutions = [QCResolution.Tick, QCResolution.Second, QCResolution.Minute, QCResolution.Hour, QCResolution.Daily]


@pytest.mark.parametrize("security_type,data_type,result", [
    (SecurityType.CFD, DataType.Quote, all_resolutions),
    (SecurityType.Crypto, DataType.Trade, all_resolutions),
    (SecurityType.Crypto, DataType.Quote, all_resolutions),
    (SecurityType.Equity, DataType.Trade, all_resolutions),
    (SecurityType.Equity, DataType.Quote, [QCResolution.Tick, QCResolution.Second, QCResolution.Minute]),
    (SecurityType.EquityOption, DataType.Trade, [QCResolution.Minute]),
    (SecurityType.EquityOption, DataType.Quote, [QCResolution.Minute]),
    (SecurityType.Forex, DataType.Quote, all_resolutions),
    (SecurityType.Future, DataType.Trade, [QCResolution.Tick, QCResolution.Second, QCResolution.Minute]),
    (SecurityType.Future, DataType.Quote, [QCResolution.Tick, QCResolution.Second, QCResolution.Minute]),
    (SecurityType.FutureOption, DataType.Trade, [QCResolution.Minute]),
    (SecurityType.FutureOption, DataType.Quote, [QCResolution.Minute]),
    (SecurityType.Index, DataType.Trade, all_resolutions),
    (SecurityType.IndexOption, DataType.Trade, [QCResolution.Minute]),
    (SecurityType.IndexOption, DataType.Quote, [QCResolution.Minute])
])
def test_security_type_get_resolutions_returns_available_resolutions(security_type: SecurityType,
                                                                     data_type: DataType,
                                                                     result: List[QCResolution]) -> None:
    assert sorted(security_type.get_resolutions(data_type)) == sorted(result)
