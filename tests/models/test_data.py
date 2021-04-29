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
from typing import List, Optional

import pytest

from lean.models.api import QCResolution
from lean.models.data import DataType, OptionStyle, SecurityDataProduct, SecurityType


@pytest.mark.parametrize("data_type,result", [(DataType.Trade, False),
                                              (DataType.Quote, False),
                                              (DataType.OpenInterest, False),
                                              (DataType.MapFactor, True),
                                              (DataType.Coarse, True)])
def test_data_type_is_resolution_returns_whether_type_is_subscription(data_type: DataType, result: bool) -> None:
    assert data_type.is_subscription() == result


@pytest.mark.parametrize("security_type,result", [(SecurityType.CFD, "Cfd"),
                                                  (SecurityType.Crypto, "Crypto"),
                                                  (SecurityType.Equity, "Equity"),
                                                  (SecurityType.EquityOption, "Option"),
                                                  (SecurityType.Forex, "Forex"),
                                                  (SecurityType.Future, "Future"),
                                                  (SecurityType.FutureOption, "FutureOption"),
                                                  (SecurityType.Index, "Index"),
                                                  (SecurityType.IndexOption, "IndexOption")])
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


@pytest.mark.parametrize("security_type,data_type,resolution,market,ticker,option_style,result", [
    # @formatter:off
    # CFD
    (SecurityType.CFD, DataType.Quote, QCResolution.Tick, "FXCM", "DE10YBEUR", None, "cfd/fxcm/tick/de10ybeur/20200615_quote.zip"),
    (SecurityType.CFD, DataType.Quote, QCResolution.Second, "FXCM", "DE10YBEUR", None, "cfd/fxcm/second/de10ybeur/20200615_quote.zip"),
    (SecurityType.CFD, DataType.Quote, QCResolution.Minute, "FXCM", "DE10YBEUR", None, "cfd/fxcm/minute/de10ybeur/20200615_quote.zip"),
    (SecurityType.CFD, DataType.Quote, QCResolution.Hour, "FXCM", "DE10YBEUR", None, "cfd/fxcm/hour/de10ybeur.zip"),
    (SecurityType.CFD, DataType.Quote, QCResolution.Daily, "FXCM", "DE10YBEUR", None, "cfd/fxcm/daily/de10ybeur.zip"),

    # Crypto
    (SecurityType.Crypto, DataType.Trade, QCResolution.Tick, "GDAX", "BTCUSD", None, "crypto/gdax/tick/btcusd/20200615_trade.zip"),
    (SecurityType.Crypto, DataType.Quote, QCResolution.Tick, "GDAX", "BTCUSD", None, "crypto/gdax/tick/btcusd/20200615_quote.zip"),
    (SecurityType.Crypto, DataType.Trade, QCResolution.Second, "GDAX", "BTCUSD", None, "crypto/gdax/second/btcusd/20200615_trade.zip"),
    (SecurityType.Crypto, DataType.Quote, QCResolution.Second, "GDAX", "BTCUSD", None, "crypto/gdax/second/btcusd/20200615_quote.zip"),
    (SecurityType.Crypto, DataType.Trade, QCResolution.Minute, "GDAX", "BTCUSD", None, "crypto/gdax/minute/btcusd/20200615_trade.zip"),
    (SecurityType.Crypto, DataType.Quote, QCResolution.Minute, "GDAX", "BTCUSD", None, "crypto/gdax/minute/btcusd/20200615_quote.zip"),
    (SecurityType.Crypto, DataType.Trade, QCResolution.Hour, "GDAX", "BTCUSD", None, "crypto/gdax/hour/btcusd_trade.zip"),
    (SecurityType.Crypto, DataType.Quote, QCResolution.Hour, "GDAX", "BTCUSD", None, "crypto/gdax/hour/btcusd_quote.zip"),
    (SecurityType.Crypto, DataType.Trade, QCResolution.Daily, "GDAX", "BTCUSD", None, "crypto/gdax/daily/btcusd_trade.zip"),
    (SecurityType.Crypto, DataType.Quote, QCResolution.Daily, "GDAX", "BTCUSD", None, "crypto/gdax/daily/btcusd_quote.zip"),

    # Equity
    (SecurityType.Equity, DataType.Trade, QCResolution.Tick, "USA", "SPY", None, "equity/usa/tick/spy/20200615_trade.zip"),
    (SecurityType.Equity, DataType.Quote, QCResolution.Tick, "USA", "SPY", None, "equity/usa/tick/spy/20200615_quote.zip"),
    (SecurityType.Equity, DataType.Trade, QCResolution.Second, "USA", "SPY", None, "equity/usa/second/spy/20200615_trade.zip"),
    (SecurityType.Equity, DataType.Quote, QCResolution.Second, "USA", "SPY", None, "equity/usa/second/spy/20200615_quote.zip"),
    (SecurityType.Equity, DataType.Trade, QCResolution.Minute, "USA", "SPY", None, "equity/usa/minute/spy/20200615_trade.zip"),
    (SecurityType.Equity, DataType.Quote, QCResolution.Minute, "USA", "SPY", None, "equity/usa/minute/spy/20200615_quote.zip"),
    (SecurityType.Equity, DataType.Trade, QCResolution.Hour, "USA", "SPY", None, "equity/usa/hour/spy.zip"),
    (SecurityType.Equity, DataType.Trade, QCResolution.Daily, "USA", "SPY", None, "equity/usa/daily/spy.zip"),

    # Equity option
    (SecurityType.EquityOption, DataType.Trade, QCResolution.Tick, "USA", "SPY", OptionStyle.American, "option/usa/tick/spy/20200615_trade_american.zip"),
    (SecurityType.EquityOption, DataType.Quote, QCResolution.Tick, "USA", "SPY", OptionStyle.American, "option/usa/tick/spy/20200615_quote_american.zip"),
    (SecurityType.EquityOption, DataType.OpenInterest, QCResolution.Tick, "USA", "SPY", OptionStyle.American, "option/usa/tick/spy/20200615_openinterest_american.zip"),
    (SecurityType.EquityOption, DataType.Trade, QCResolution.Second, "USA", "SPY", OptionStyle.American, "option/usa/second/spy/20200615_trade_american.zip"),
    (SecurityType.EquityOption, DataType.Quote, QCResolution.Second, "USA", "SPY", OptionStyle.American, "option/usa/second/spy/20200615_quote_american.zip"),
    (SecurityType.EquityOption, DataType.OpenInterest, QCResolution.Second, "USA", "SPY", OptionStyle.American, "option/usa/second/spy/20200615_openinterest_american.zip"),
    (SecurityType.EquityOption, DataType.Trade, QCResolution.Minute, "USA", "SPY", OptionStyle.American, "option/usa/minute/spy/20200615_trade_american.zip"),
    (SecurityType.EquityOption, DataType.Quote, QCResolution.Minute, "USA", "SPY", OptionStyle.American, "option/usa/minute/spy/20200615_quote_american.zip"),
    (SecurityType.EquityOption, DataType.OpenInterest, QCResolution.Minute, "USA", "SPY", OptionStyle.American, "option/usa/minute/spy/20200615_openinterest_american.zip"),
    (SecurityType.EquityOption, DataType.Trade, QCResolution.Hour, "USA", "SPY", OptionStyle.American, "option/usa/hour/spy_trade_american.zip"),
    (SecurityType.EquityOption, DataType.Quote, QCResolution.Hour, "USA", "SPY", OptionStyle.American, "option/usa/hour/spy_quote_american.zip"),
    (SecurityType.EquityOption, DataType.OpenInterest, QCResolution.Hour, "USA", "SPY", OptionStyle.American, "option/usa/hour/spy_openinterest_american.zip"),
    (SecurityType.EquityOption, DataType.Trade, QCResolution.Daily, "USA", "SPY", OptionStyle.American, "option/usa/daily/spy_trade_american.zip"),
    (SecurityType.EquityOption, DataType.Quote, QCResolution.Daily, "USA", "SPY", OptionStyle.American, "option/usa/daily/spy_quote_american.zip"),
    (SecurityType.EquityOption, DataType.OpenInterest, QCResolution.Daily, "USA", "SPY", OptionStyle.American, "option/usa/daily/spy_openinterest_american.zip"),

    # Forex
    (SecurityType.Forex, DataType.Quote, QCResolution.Tick, "Oanda", "EURUSD", None, "forex/oanda/tick/eurusd/20200615_quote.zip"),
    (SecurityType.Forex, DataType.Quote, QCResolution.Second, "Oanda", "EURUSD", None, "forex/oanda/second/eurusd/20200615_quote.zip"),
    (SecurityType.Forex, DataType.Quote, QCResolution.Minute, "Oanda", "EURUSD", None, "forex/oanda/minute/eurusd/20200615_quote.zip"),
    (SecurityType.Forex, DataType.Quote, QCResolution.Hour, "Oanda", "EURUSD", None, "forex/oanda/hour/eurusd.zip"),
    (SecurityType.Forex, DataType.Quote, QCResolution.Daily, "Oanda", "EURUSD", None, "forex/oanda/daily/eurusd.zip"),

    # Future
    (SecurityType.Future, DataType.Trade, QCResolution.Tick, "NYMEX", "A0D", None, "future/nymex/tick/a0d/20200615_trade.zip"),
    (SecurityType.Future, DataType.Quote, QCResolution.Tick, "NYMEX", "A0D", None, "future/nymex/tick/a0d/20200615_quote.zip"),
    (SecurityType.Future, DataType.OpenInterest, QCResolution.Tick, "NYMEX", "A0D", None, "future/nymex/tick/a0d/20200615_openinterest.zip"),
    (SecurityType.Future, DataType.Trade, QCResolution.Second, "NYMEX", "A0D", None, "future/nymex/second/a0d/20200615_trade.zip"),
    (SecurityType.Future, DataType.Quote, QCResolution.Second, "NYMEX", "A0D", None, "future/nymex/second/a0d/20200615_quote.zip"),
    (SecurityType.Future, DataType.OpenInterest, QCResolution.Second, "NYMEX", "A0D", None, "future/nymex/second/a0d/20200615_openinterest.zip"),
    (SecurityType.Future, DataType.Trade, QCResolution.Minute, "NYMEX", "A0D", None, "future/nymex/minute/a0d/20200615_trade.zip"),
    (SecurityType.Future, DataType.Quote, QCResolution.Minute, "NYMEX", "A0D", None, "future/nymex/minute/a0d/20200615_quote.zip"),
    (SecurityType.Future, DataType.OpenInterest, QCResolution.Minute, "NYMEX", "A0D", None, "future/nymex/minute/a0d/20200615_openinterest.zip"),
    (SecurityType.Future, DataType.Trade, QCResolution.Hour, "NYMEX", "A0D", None, "future/nymex/hour/a0d_trade.zip"),
    (SecurityType.Future, DataType.Quote, QCResolution.Hour, "NYMEX", "A0D", None, "future/nymex/hour/a0d_quote.zip"),
    (SecurityType.Future, DataType.OpenInterest, QCResolution.Hour, "NYMEX", "A0D", None, "future/nymex/hour/a0d_openinterest.zip"),
    (SecurityType.Future, DataType.Trade, QCResolution.Daily, "NYMEX", "A0D", None, "future/nymex/daily/a0d_trade.zip"),
    (SecurityType.Future, DataType.Quote, QCResolution.Daily, "NYMEX", "A0D", None, "future/nymex/daily/a0d_quote.zip"),
    (SecurityType.Future, DataType.OpenInterest, QCResolution.Daily, "NYMEX", "A0D", None, "future/nymex/daily/a0d_openinterest.zip"),

    # Future option
    (SecurityType.FutureOption, DataType.Trade, QCResolution.Minute, "CME", "ES", OptionStyle.American, "futureoption/cme/minute/es/20200620/20200615_trade_american.zip"),
    (SecurityType.FutureOption, DataType.Quote, QCResolution.Minute, "CME", "ES", OptionStyle.American, "futureoption/cme/minute/es/20200620/20200615_quote_american.zip"),
    (SecurityType.FutureOption, DataType.OpenInterest, QCResolution.Minute, "CME", "ES", OptionStyle.American, "futureoption/cme/minute/es/20200620/20200615_openinterest_american.zip"),

    # Index
    (SecurityType.Index, DataType.Trade, QCResolution.Tick, "USA", "SPX", None, "index/usa/tick/spx/20200615_trade.zip"),
    (SecurityType.Index, DataType.Trade, QCResolution.Second, "USA", "SPX", None, "index/usa/second/spx/20200615_trade.zip"),
    (SecurityType.Index, DataType.Trade, QCResolution.Minute, "USA", "SPX", None, "index/usa/minute/spx/20200615_trade.zip"),
    (SecurityType.Index, DataType.Trade, QCResolution.Hour, "USA", "SPX", None, "index/usa/hour/spx.zip"),
    (SecurityType.Index, DataType.Trade, QCResolution.Daily, "USA", "SPX", None, "index/usa/daily/spx.zip"),

    # Index option
    (SecurityType.IndexOption, DataType.Trade, QCResolution.Tick, "USA", "SPX", OptionStyle.European, "indexoption/usa/tick/spx/20200615_trade_european.zip"),
    (SecurityType.IndexOption, DataType.Quote, QCResolution.Tick, "USA", "SPX", OptionStyle.European, "indexoption/usa/tick/spx/20200615_quote_european.zip"),
    (SecurityType.IndexOption, DataType.OpenInterest, QCResolution.Tick, "USA", "SPX", OptionStyle.European, "indexoption/usa/tick/spx/20200615_openinterest_european.zip"),
    (SecurityType.IndexOption, DataType.Trade, QCResolution.Second, "USA", "SPX", OptionStyle.European, "indexoption/usa/second/spx/20200615_trade_european.zip"),
    (SecurityType.IndexOption, DataType.Quote, QCResolution.Second, "USA", "SPX", OptionStyle.European, "indexoption/usa/second/spx/20200615_quote_european.zip"),
    (SecurityType.IndexOption, DataType.OpenInterest, QCResolution.Second, "USA", "SPX", OptionStyle.European, "indexoption/usa/second/spx/20200615_openinterest_european.zip"),
    (SecurityType.IndexOption, DataType.Trade, QCResolution.Minute, "USA", "SPX", OptionStyle.European, "indexoption/usa/minute/spx/20200615_trade_european.zip"),
    (SecurityType.IndexOption, DataType.Quote, QCResolution.Minute, "USA", "SPX", OptionStyle.European, "indexoption/usa/minute/spx/20200615_quote_european.zip"),
    (SecurityType.IndexOption, DataType.OpenInterest, QCResolution.Minute, "USA", "SPX", OptionStyle.European, "indexoption/usa/minute/spx/20200615_openinterest_european.zip"),
    (SecurityType.IndexOption, DataType.Trade, QCResolution.Hour, "USA", "SPX", OptionStyle.European, "indexoption/usa/hour/spx_trade_european.zip"),
    (SecurityType.IndexOption, DataType.Quote, QCResolution.Hour, "USA", "SPX", OptionStyle.European, "indexoption/usa/hour/spx_quote_european.zip"),
    (SecurityType.IndexOption, DataType.OpenInterest, QCResolution.Hour, "USA", "SPX", OptionStyle.European, "indexoption/usa/hour/spx_openinterest_european.zip"),
    (SecurityType.IndexOption, DataType.Trade, QCResolution.Daily, "USA", "SPX", OptionStyle.European, "indexoption/usa/daily/spx_trade_european.zip"),
    (SecurityType.IndexOption, DataType.Quote, QCResolution.Daily, "USA", "SPX", OptionStyle.European, "indexoption/usa/daily/spx_quote_european.zip"),
    (SecurityType.IndexOption, DataType.OpenInterest, QCResolution.Daily, "USA", "SPX", OptionStyle.European, "indexoption/usa/daily/spx_openinterest_european.zip"),
    # @formatter:on
])
def test_security_data_product_get_relative_path_returns_correct_path(security_type: SecurityType,
                                                                      data_type: DataType,
                                                                      resolution: QCResolution,
                                                                      market: str,
                                                                      ticker: str,
                                                                      option_style: Optional[OptionStyle],
                                                                      result: str) -> None:
    product = SecurityDataProduct(data_type=data_type,
                                  security_type=security_type,
                                  market=market,
                                  resolution=resolution,
                                  ticker=ticker,
                                  start_date=datetime(2020, 6, 14),
                                  end_date=datetime(2020, 6, 16),
                                  option_style=option_style,
                                  expiry_dates_by_data_date=None)

    data_date = datetime(2020, 6, 15)
    expiry_date = datetime(2020, 6, 20) if security_type == SecurityType.FutureOption else None

    assert product.get_relative_path(data_date, expiry_date).as_posix() == result
