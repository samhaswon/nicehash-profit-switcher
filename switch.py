import subprocess
import os
import requests
from signal import SIGINT, SIGTERM
from time import sleep

class NH_API_Calls(object):
    """Handler for Nicehash api calls"""
    def __init__(self, host) -> None:
        """:param host = the api to be queried"""
        self.host = host

    def request(self, method: str, path: str):
        """
        :param method = http request method
        :param path = path from host (defined during initialization)
        : 
        """
        url = self.host + path

        s = requests.Session()
        response = s.request(method.upper(), url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(str(response.status_code) + ": " + 
                response.reason + ": " + str(response.content))
        else:
            raise Exception(str(response.status_code) + ": " + 
                response.reason)

    def get_multialgo_info(self):
        """Gets the paying rate of all nicehash algorithms in a json format"""
        return self.request('GET', '/main/api/v2/public/simplemultialgo/info/')
    
    def get_prices(self):
        return self.request('GET', '/exchange/api/v2/info/prices')


class Switch_Info(object):
    """Gets the information needed for the most profitable algorithm to mine"""

    def __init__(self, 
        host = 'https://api2.nicehash.com', switch_minutes = 1,
        algos = {"etchash": [71500000, 0]}, switch_override_pct = 20
    ) -> None:
        """ :param host = the api to be queried
            :param switch_minutes = minutes to wait before switching
            :param algos = Dictionary of the format "name": [speed, pay (set
             to 0)]
            :param switch_override_pct = time override for switching in 
             percent (20% would be input as 20)
        """
        
        self.switch_minutes = switch_minutes
        self.switch_minutes_left = self.switch_minutes
        self.algos = algos
        self.current_algo = ""
        self.switch_override_pct = switch_override_pct * 0.01
        self.NH_Query: NH_API_Calls = NH_API_Calls(host)

    def get_algo_info(self) -> dict:
        """api query for algo info"""
        try:
            algo_stats = self.NH_Query.get_multialgo_info()

            # Parse response to dictionary
            return {algorithm['algorithm'].lower(): float(algorithm['paying'])
                    for algorithm in algo_stats['miningAlgorithms']}
        except Exception as ex:
            print("Unexpected error: ", ex)
            sleep(5)
            return self.get_algo_info()

    def get_btc_price(self) -> float:
        """query the API for BTC price"""
        try:
            response = self.NH_Query.get_prices()
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
        """Print algos and their profitability in sat and USDT"""
        print("")
        for algo, stats in self.algos.items():
            print("{0: <16}".format(algo), ":", "{0: >4}".format(stats[1]), 
                "sat or ${:0.2f}".format(stats[1] / 100000000 * btc_price))

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
        print("\n{} is the most profitable at {}sat/day\n".format(
                most_profitable, self.algos[most_profitable][1]))

        # Figure out which algo to mine
        if self.current_algo is None:
            self.current_algo = most_profitable
            return self.current_algo

        elif (self.current_algo is not most_profitable and 
                self.switch_minutes_left > 0):
            # Faster switching for significantly higher profit algo
            if (self.algos[most_profitable][1] > 
                    self.algos[self.current_algo][1] * (1 + 
                    self.switch_override_pct)):
                self.current_algo = most_profitable
                self.switch_minutes_left = self.switch_minutes
                return self.current_algo
            else:
                self.switch_minutes_left -= 1
                return self.current_algo
        
        elif (self.current_algo is not most_profitable and 
                self.switch_minutes_left <= 0):
            self.switch_minutes_left = self.switch_minutes
            self.current_algo = most_profitable
            return self.current_algo

        else:
            self.switch_minutes_left = self.switch_minutes
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
        self.current_algo: str = ""
        self.current_miner: subprocess.Popen = None
        self.cmd_type: str = cmd_type


    def run_miner(self, name: str) -> None:
        if self.current_miner is None:
            print("Starting {}...".format(name))
            self.current_miner = subprocess.Popen([self.cmd_type, 
                self.comands[name]], preexec_fn=os.setsid)
        
        else:
            self.stop()
            print("Starting {}...".format(name))
            self.current_miner = subprocess.Popen([self.cmd_type, 
                self.comands[name]], preexec_fn=os.setsid)

    def stop(self) -> None:
        # Send the keyboard interupt signal then wait
        try:
            print("Killing...")
            os.killpg(os.getpgid(self.current_miner.pid), SIGINT)
            sleep(2)
        except Exception as ex:
            print("Error: {}".format(ex))
            self.current_miner.kill()
        

    def set_current(self, name: str) -> None:
        if (name != self.current_algo):
            self.run_miner(name)
            self.current_algo = name

    def __del__(self) -> None:
    	if self.current_algo != None:
        	self.stop()