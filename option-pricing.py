import numpy as np
import scipy.stats as si
import mibian
import math


class OptionPricing(object):
    pass

    def __init__(self):
        S_0 = 419.62
        K = 410
        T = 29           # Measured in days
        r = 0.67
        sigma = 99.58
        div = 0
        self.option = 'call'
        h = 0.25
        N = 10

        # Choose between expected or current option value
        self.value_type = 'expect_value'

        
        # print(self.binomial_option_tree(900, 900, T, 0.0025, 0.25784, h, N))
        # print(self.binomial_option_tree(S_0, K, T, r, sigma, h, N))
        detailed_list = self.binomial_option_tree(S_0, K, T, r, sigma, h, N)
        self.print_tree(detailed_list)
        dash = '-' * 40
        print('\n')
        print(dash)
        print(f"Calculated BS-score (formula): {self.call_put_pricing(S_0, K, T, r, sigma, div, self.option)}")
        print(f"Calculated BS-score (Mibian): {self.call_put_pricing_mibian(S_0, K, T, r, sigma, div, self.option)}")

    def call_put_pricing(self, S_0, K, T, r, sigma, div, option='call'):
        """
        Function for pricing put and call options. 
        C(S,t) = SN(d1) - Ke^(-r(T-t)) * N(d2)
        P(S,t) = Ke^(-r(T-t)) * N(-d2) - SN(-d1)
        Where d1 = (ln(S/K) + (r + (sigma^2 / 2)) * (T-t)) / (sigma * sqrt(T-t))
        and   d2 = (d1 - sigma * sqrt(T-t) = (ln(S/K) + (r - (sigma^2 / 2) * (T-t)) / (sigma * sqrt(T-t))
        :param: S_0 -> current price of stock
        :param: K -> Exercise price
        :param: T -> Time to maturity (defined as T - t) where T in years
        :param: r -> risk-free rate
        :param: sigma -> volatility sigma
        :param: div -> dividend yield
        :param: Option -> either put or call
        :return: Correct option price
        """
        T = T / 365        # Convert to days
        r = r / 100         # Convert to decimals
        sigma = sigma / 100     # Convert to decimals

        d1 = (np.log(S_0 / K) + (r - div + 0.5 * sigma ** 2) * T) / \
            (sigma * np.sqrt(T))
        d2 = (np.log(S_0 / K) + (r - div - 0.5 * sigma ** 2) * T) / \
            (sigma * np.sqrt(T))

        if option == 'call':
            result = (S_0 * np.exp(-div * T) * si.norm.cdf(d1, 0.0,
                                                           1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
        elif option == 'put':
            result = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) -
                      S_0 * np.exp(-div * T) * si.norm.cdf(-d1, 0.0, 1.0))
        else:
            raise NameError('Option not defined correctly')

        return result

    def call_put_pricing_mibian(self, S_0, K, T, r, sigma, div, option='call'):
        c = mibian.BS([S_0, K, r, T], volatility=sigma)

        if option == 'call':
            return c.callPrice
        elif option == 'put':
            return c.putPrice
        else:
            raise NameError('Option not defined correctly')

    def binomial_option_tree(self, S_0, K, T, r, sigma, h, N):
        r = r / 100
        sigma = sigma / 100
        h = T / 365
        u, d = self.std_dev_up_down(sigma, h)
        p = self.calculate_p(r, u, d)

        layer_list = []
        layer_list.append([S_0])
        detailed_tree = []

        for i in range(N):
            prev_prices = layer_list[i]
            new_prices = set()
            detailed_tree_layer = []
            for price in prev_prices:
                next_up, next_down = self.calculate_next_prices(price, u, d)
                new_prices.add(next_up)
                new_prices.add(next_down)

                node = {}
                node['layer'] = i
                node['price'] = price

                max_stock = next_up
                min_stock = next_down
                max_option = next_up - K
                min_option = next_down - K
                if self.option == 'call':
                    if min_option < 0:
                        min_option = 0
                    if max_option < 0:
                        max_option = 0

                stock_spread = max_stock - min_stock
                option_spread = max_option - min_option

                expected_value = (p * max_option) + (1-p * min_option)
                if self.option == 'call':
                    if expected_value < 0:
                        expected_value = 0
                elif self.option == 'put':
                    if expected_value > 0:
                        expected_value = 0

                node['expect_value'] = expected_value
                node['current_value'] = expected_value / (1 + r)
                try:
                    node['option_delta'] = option_spread / stock_spread
                except ZeroDivisionError:
                    node['option_delta'] = 0.0
                node['next_up'] = next_up
                node['next_down'] = next_down
                node['min_option'] = min_option
                node['max_option'] = max_option
                node['stock_spread'] = stock_spread
                node['option_spread'] = option_spread
                detailed_tree_layer.append(node)

            sorted_new_prices = sorted(new_prices)
            layer_list.append(sorted(new_prices))
            detailed_tree.append(detailed_tree_layer)

        last_tree_layer = []
        for price in layer_list[-1]:
            last_node = {}
            last_node['layer'] = len(layer_list) - 1
            last_node['price'] = price

            expected_value = p * (price - K)
            if expected_value < 0:
                expected_value = 0
            current_value = expected_value / (1 + r)
            last_node['expect_value'] = expected_value
            last_node['current_value'] = current_value
            last_tree_layer.append(last_node)
        detailed_tree.append(last_tree_layer)
        return detailed_tree

    def print_tree(self, detailed_list):
        last_layer = 0
        price_list = []
        option_list = []
        delta_list = []

        layer_prices = []
        layer_options = []
        layer_deltas = []

        node_index = 0
        for layer in detailed_list:
            layer_prices = []
            layer_options = []
            layer_deltas = []

            for node in layer:
                current_layer = node['layer']

                layer_prices.append(node['price'])
                layer_options.append(node[self.value_type])
                try:
                    layer_deltas.append(node['option_delta'])
                except KeyError:            # Last row does not contain option_delta header
                    layer_deltas = []
            self.format_prints(current_layer, layer_prices,
                               layer_options, layer_deltas)

    def format_prints(self, current_layer, price_list, option_list, delta_list):
        # for i in range(len(price_list)):
        dash = '-' * 60
        print(dash)
        print(f"Layer: {current_layer}")
        print(dash)
        price_string = 'Expected stock prices: '
        for j in range(len(price_list)):
            price = price_list[j]
            price_string += '{}{:<4}'.format(price, ' ')
        print(price_string)

        option_string = 'Expected option prices: '
        for j in range(len(option_list)):
            option = round(option_list[j], 2)
            option_string += '{}{:<4}'.format(option, ' ')
        print(option_string)

        delta_string = 'Calculated delta values: '
        for j in range(len(delta_list)):
            delta = round(delta_list[j], 5)
            delta_string += '{}{:<4}'.format(delta, ' ')
        print(delta_string)

    def std_dev_up_down(self, sigma, h):
        """
        Calculate the up and down changes from the standard deviation of a stock
        :param: sigma -> standard deviation of stock
        :param: h -> fraction of a year (timestep)
        :return: up and down changes in decimals
        """
        u = math.exp(sigma * math.sqrt(h))
        d = 1 / u
        return u, d

    def calculate_p(self, r, u, d):
        """ 
        p = (interest rate - downside change) / (upside change - downside change)
        :param: r -> interest rate
        :param: u -> upside change
        :param: d -> downside change
        """
        d -= 1
        u -= 1

        p = (r - d) / (u - d)
        return p

    def calculate_spread(self):
        pass

    def calculate_next_prices(self, S_0, u, d):
        next_up = S_0 * u
        next_down = S_0 * d
        return round(next_up, 2), round(next_down, 2)

if __name__ == "__main__":
    option_pricer = OptionPricing()
