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
        option = 'call'

        print(self.call_put_pricing(S_0, K, T, r, sigma, div, option))
        print(self.call_put_pricing_mibian(S_0, K, T, r, sigma, div, option))


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

    def binomial_option_tree(self, r, sigma, h):

        u, d = self.std_dev_up_down(sigma, h)
        self.calculate_p(r, u, d)

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
        p = (r - d) / (u - d)
        return p
        



if __name__ == "__main__":
    option_pricer = OptionPricing()
