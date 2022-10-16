import nicehash
import subprocess
from signal import SIGINT, SIGTERM
from time import sleep

class Switch_Info(object):
    """Gets the information needed for the most profitable algorithm to mine"""

    def __init__(
        self, host = 'https://api2.nicehash.com', switch_minutes = 1,
        algos = {"kawpow": [32400000, 0], "zelhash": [63, 0], 
            "daggerhashimoto": [71500000, 0], "autolykos": [165500000, 0],
            "etchash": [71500000, 0]}
    ) -> None:
        """ :param host = the api to be queried
            :param switch_minutes = minutes to wait before switching
            :param algos = Dictionary of the format "name": [speed, pay (set to 0)]
        """
        
        self.host = host
        self.switch_minutes = switch_minutes
        self.switch_minutes_left = self.switch_minutes
        self.algos = algos
        self.current_algo = None

    def get_algo_info(self):
        """api query for algo info"""
        try:
            public_api = nicehash.public_api(self.host, False)
            algo_stats = public_api.get_multialgo_info()

            # Parse response to dictionary
            return {algorithm['algorithm'].lower(): float(algorithm['paying'])
                    for algorithm in algo_stats['miningAlgorithms']}
        except Exception as ex:
            print("Unexpected error: ", ex)
            sleep(5)
            return self.get_algo_info(self)

    def get_btc_price(self) -> float:
        """query the API for BTC price"""
        try:
            public_api = nicehash.public_api(self.host, False)
            response = public_api.request('GET', '/exchange/api/v2/info/prices'
                                            , '', None)
        except Exception as ex:
            print("Unexpected error: ", ex)
            sleep(5)
            return self.get_btc_price()

        # Parse and return the response
        return float(response['BTCUSDT'])

    def get_most_profit(self, algos: dict) -> str:
        """Returns the current most profitable coin"""
        # Grab the first key
        name = list(algos.keys())[0]

        # Find the most profitable algo
        for algo, stats in algos.items():
            if algos[name][1] < stats[1]:
                name = algo
        
        return name

    def print_algos(self, btc_price: float) -> None:
        """Print algos and their profitability in mBTC and USDT"""
        for algo, stats in self.algos.items():
            print("{0: <16}".format(algo), ":", "{0: >4}".format(stats[1]), 
                "mBTC or ${:0.2f}".format(stats[1] / 100000000 * btc_price, 2))

    def set_profits(self, algos: dict, algo_stats: dict) -> None:
        """Set the profitability of each algorithm in algos, originally 0"""
        for algo, stats in algos.items():
            stats[1] = int(algo_stats[algo] * stats[0])

    def algo_to_mine(self) -> str:
        """ :return the algo name that should be currently mined.
            MUST be externally limited to avoid excessive API calls!
        """
        # API calling for stats
        algo_stats = self.get_algo_info()
        btc_price = self.get_btc_price()
        self.set_profits(self.algos, algo_stats)

        # Algos printing
        self.print_algos(btc_price)
        most_profitable = self.get_most_profit(self.algos)
        print("\n{} is the most profitable at {}mBTC/day\n".format(
                most_profitable, self.algos[most_profitable][1]))

        # Figure out which algo to mine
        if self.current_algo is None:
            self.current_algo = most_profitable
            return self.current_algo

        elif (self.current_algo is not most_profitable and 
                self.switch_minutes_left > 0):
            self.switch_minutes_left -= 1
            return self.current_algo
        
        elif (self.current_algo is not most_profitable and 
                self.switch_minutes_left <= 0):
            self.switch_minutes_left = self.switch_minutes
            self.current_algo = most_profitable
            return self.current_algo

        else:
            return most_profitable

class Switch_Thread(object):
    """A wrapper for miner switching"""

    def __init__(self, commands: dict, cmd_type: str) -> None:
        """ :param commands = dictionary of key value pairs of algo_name: 
             algo_command. algo_command must be one argument (the call)
            :param cmd_type = what you would prepend the command with to run 
             it in your OS (i.e., ./ or .\ or bash or etc.)
        """
        self.comands: dict = commands
        self.current_algo: str = None
        self.current_miner: subprocess.Popen = None
        self.cmd_type: str = cmd_type


    def run_miner(self, name: str) -> None:
        if self.current_miner is None:
            self.current_miner = subprocess.Popen([self.cmd_type, 
                self.comands[name]])
        
        else:
            self.stop()
            self.current_miner = subprocess.Popen([self.cmd_type, 
                self.comands[name]])

    def stop(self) -> None:
        # Send the keyboard interupt signal then wait
        self.current_miner.send_signal(SIGINT)
        self.current_miner.wait(timeout=30)

    def set_current(self, name: str) -> None:
        if (name != self.current_algo):
            self.run_miner(name)
            self.current_algo = name

    def __del__(self):
        if self.current_algo != None:
            self.stop()
