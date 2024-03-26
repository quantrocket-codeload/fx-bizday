# Copyright 2020-2024 QuantRocket LLC - All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
from moonshot import Moonshot
from moonshot.commission import SpotFXCommission

class FxBizday(Moonshot):

    CODE = "fx-bizday"
    DB = "fiber-1h"
    DB_FIELDS = ["Close"]
    COMMISSION_CLASS = SpotFXCommission
    SLIPPAGE_BPS = 0.1
    SIDS = "FXEURUSD"
    BENCHMARK = "FXEURUSD"
    SELL_EUR_START = "03:00:00"
    SELL_EUR_END = "11:00:00"
    BUY_EUR_START = "11:00:00"
    BUY_EUR_END = "16:00:00"

    def prices_to_signals(self, prices: pd.DataFrame):

        closes = prices.loc["Close"]

        # Get a DataFrame of times
        times = closes.index.get_level_values("Time")
        times = closes.apply(lambda x: times)

        # Sell EUR.USD when Europe is open and US is closed
        sell_eur = (times >= self.SELL_EUR_START) & (times < self.SELL_EUR_END)

        # Buy EUR.USD when Europe is closed and US is open
        buy_eur = (times >= self.BUY_EUR_START) & (times < self.BUY_EUR_END)

        # Construct 1s and -1s with which to create our signals DataFrame
        ones = pd.DataFrame(1, index=closes.index, columns=closes.columns)
        minus_ones = pd.DataFrame(-1, index=closes.index, columns=closes.columns)

        # Create int signals from booleans
        signals = minus_ones.where(sell_eur, ones.where(buy_eur, 0))

        # Only on weekdays
        are_weekdays = closes.index.get_level_values("Date").day_name().isin([
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday"
        ])
        are_weekdays = signals.apply(lambda x: are_weekdays)
        signals = signals.where(are_weekdays, 0)

        return signals

    def signals_to_target_weights(self, signals: pd.DataFrame, prices: pd.DataFrame):
        # Assign 100% of capital to signal
        weights = signals.copy()
        return weights

    def target_weights_to_positions(self, weights: pd.DataFrame, prices: pd.DataFrame):
        # Enter the position the same period
        positions = weights.copy()
        return positions

    def positions_to_gross_returns(self, positions: pd.DataFrame, prices: pd.DataFrame):
        closes = prices.loc["Close"]
        gross_returns = closes.pct_change() * positions.shift()
        return gross_returns

    def order_stubs_to_orders(self, orders: pd.DataFrame, prices: pd.DataFrame):
        orders["Exchange"] = "IDEALPRO"
        orders["OrderType"] = "MKT"
        orders["Tif"] = "DAY"

        return orders
