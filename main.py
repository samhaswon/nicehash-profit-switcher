import nicehash
import os
import signal
import subprocess
from time import sleep

host = 'https://api2.nicehash.com'
#host = 'https://api-test.nicehash.com'
# Minutes + 1 new most profitable must be profitable
switch_minutes = 2
   

def get_algo_info():
    # api query
    try:
        public_api = nicehash.public_api(host, False)
        algo_stats = public_api.get_multialgo_info()

        # Parse response to dictionary
        return {algorithm['algorithm'].lower(): float(algorithm['paying'])
                for algorithm in algo_stats['miningAlgorithms']}
    except Exception as ex:
        print("Unexpected error: ", ex)
        return None

def get_algo_profitability(name: str, factor: float, algo_stats: dict,) -> int:
    return int(algo_stats[name] * factor)

def get_btc_price() -> float:
    # Query the API
    try:
        public_api = nicehash.public_api(host, False)
        response = public_api.request('GET', '/exchange/api/v2/info/prices', '', None)
    except Exception as ex:
        print("Unexpected error: ", ex)
        return -1

    # Parse and return the response
    return float(response['BTCUSDT'])

def get_most_profit(algo_stats: dict, algos: dict) -> str:
    # Grab the first key
    name = list(algos.keys())[0]

    # Find the most profitable algo
    for algo, stats in algos.items():
        if algos[name][1] < stats[1]:
            name = algo
    
    return name

def print_algos(btc_price: float) -> None:
    # Print algos and their profitability in mBTC and USDT
    for algo, stats in algos.items():
        print("{0: <16}".format(algo), ":", "{0: >4}".format(stats[1]), 
            "mBTC or ${:0.2f}".format(stats[1] / 100000000 * btc_price, 2))

def set_profits(algos: dict, algo_stats: dict) -> None:
    for algo, stats in algos.items():
        stats[1] = get_algo_profitability(algo, stats[0], algo_stats)



if __name__ == "__main__":
    # Info for the algos in the format  name: [(sat/[H/Sol/G]), pay(set to 0)]
    algos = {"kawpow": [32400000, 0], "zelhash": [63, 0], "daggerhashimoto": [71500000, 0], "autolykos": [165500000, 0]}
    # Commands for the above algos in the format  name: command
    commands = {"kawpow": "py delete.py", "zelhash": "py delete.py", "daggerhashimoto": "py delete.py", "autolykos": "py delete.py"}

    switch_to_algo = None, 0
    current_algo = None
    miner_pid = None

    # Main running loop
    while (True):
        try:
            algo_stats = get_algo_info()
            btc_price = get_btc_price()
            set_profits(algos, algo_stats)
            most_profitable = get_most_profit(algo_stats, algos)

            print_algos(btc_price)
            print("\n{} is the most profitable at {}mBTC/day\n".format(most_profitable, algos[most_profitable][1]))

            if current_algo is None:
                current_algo = most_profitable
                out = subprocess.Popen(commands[current_algo], stderr=subprocess.STDOUT, shell=True)
                miner_pid = out.pid
                print("Starting {}...".format(current_algo))

            elif current_algo is not most_profitable and switch_to_algo[1] < switch_minutes:
                if switch_to_algo[0] is most_profitable:
                    switch_to_algo = switch_to_algo[0], switch_to_algo[1] + 1
                else:
                    switch_to_algo = most_profitable, 1

                print("Still running {} for {} more minutes".format(current_algo, switch_minutes - switch_to_algo[1]))

            elif current_algo is not most_profitable and switch_to_algo[1] >= switch_minutes:
                print("Killing {}...".format(current_algo))
                os.kill(miner_pid, signal.SIGINT)
                current_algo = most_profitable
                out = subprocess.Popen(commands[current_algo], stderr=subprocess.STDOUT, shell=True)
                miner_pid = out.pid
                print("Starting {}...".format(current_algo))
            
            else:
                print("Running: {}".format(current_algo))

            sleep(60)

        # End program on CTRL + C
        except KeyboardInterrupt:
            print("Ending...")

            # Kill the running miner if program crashes
            if miner_pid is not None:
                os.kill(miner_pid, signal.SIGINT)

            exit(0)
