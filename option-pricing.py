import numpy as np
import scipy.stats as si
import mibian
import math

class OptionPricing(object):
    pass

    def __init__(self):
        S_0 = 419.62
        K = 410
        T = 4           # Measured in days
        r = 0.67
        sigma = 99.58
        div = 0
        self.option = 'call'
        h = 0.25
        N = 10

        print(self.call_put_pricing(S_0, K, T, r, sigma, div, self.option))
        print(self.call_put_pricing_mibian(S_0, K, T, r, sigma, div, self.option))
        # print(self.binomial_option_tree(900, 900, T, 0.0025, 0.25784, h, N))
        # print(self.binomial_option_tree(S_0, K, T, r, sigma, h, N))
        detailed_list = self.binomial_option_tree(S_0, K, T, r, sigma, h, N)
        print(self.print_tree(detailed_list))



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
        h = 1 / 365
        u, d = self.std_dev_up_down(sigma, h)
        p = self.calculate_p(r, u, d)

        layer_list = []
        layer_list.append([S_0])
        detailed_tree = []

        for i in range(N):            # -1 to let N reflect the amnt of layers
            prev_prices = layer_list[i]
            new_prices =  set()
            for price in prev_prices:
                next_up, next_down = self.calculate_next_prices(price, u, d)             
                new_prices.add(next_up)
                new_prices.add(next_down)

                node = {}
                node['layer'] = i
                node['price'] = price
                expect_value = p * (price - K)
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

                node['expect_value'] = expect_value
                node['current_value'] = expect_value / (1 + r)
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
                detailed_tree.append(node)

            sorted_new_prices = sorted(new_prices)         
            layer_list.append(sorted(new_prices))
        return detailed_tree

    def print_tree(self, detailed_list):
        last_layer = 0
        price_list = []
        option_list = []
        delta_list = []

        layer_prices = []
        layer_options = []
        layer_deltas = []

        for node in detailed_list:
            
            current_layer = node['layer']
            if last_layer < current_layer:
                price_list.append(layer_prices)
                option_list.append(layer_options)
                delta_list.append(layer_deltas)

                layer_prices = []
                layer_options = []
                layer_deltas = []

            layer_prices.append(node['price'])
            layer_options.append(node['expect_value'])
            layer_deltas.append(node['option_delta'])
    
            last_layer = current_layer
        
        for i in range(len(price_list)):
            dash = '-' * 60
            print(dash)
            print(f"Layer: {i}")
            print(dash)
            price_string = ''
            for j in range(len(price_list[i])):
                price = price_list[i][j]
                price_string += f'{price}     '
            print(price_string)

            option_string = ''
            for j in range(len(price_list[i])):
                option = round(option_list[i][j], 2)
                option_string += f'{option}     '
            print(option_string)

            delta_string = ''
            for j in range(len(price_list[i])):
                delta = round(delta_list[i][j], 5)
                delta_string += f'{delta}     '
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
    
