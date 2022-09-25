from typing import Dict
import nicehash
import os
import signal
import subprocess
from time import sleep

host = 'https://api2.nicehash.com'
#host = 'https://api-test.nicehash.com'


def response_parse(response) -> Dict:
    return {algorithm['algorithm'].lower(): float(algorithm['paying'])
            for algorithm in response['miningAlgorithms']}

def get_algo_info() -> dict:
    # api query
    public_api = nicehash.public_api(host, False)
    algo_stats = public_api.get_multialgo_info()

    # Parse response to dictionary
    algos = response_parse(algo_stats)
    return algos

def get_btc_price() -> float:
    # Query the API
    public_api = nicehash.public_api(host, False)
    response = public_api.request('GET', '/exchange/api/v2/info/prices', '', None)

    # Parse and return the response
    return float(response['BTCUSDT'])

def print_algos(algo_stats: dict, btc_price: float) -> None:
    # Print algos and their profitability in mBTC and USDT
    for algo, stats in algos.items():
        stats[1] = get_algo_profitability(algo, stats[0], algo_stats)
        print("{0: <16}".format(algo), ":", "{0: >4}".format(stats[1]), 
            "mbtc or ${:0.2f}".format(stats[1] / 100000000 * btc_price, 2))

def get_algo_profitability(name: str, factor: float, algo_stats: dict,) -> int:
    return int(algo_stats[name] * factor)


if __name__ == "__main__":
    algos = {"kawpow": [32400000, 0], "zelhash": [63, 0], "daggerhashimoto": [71500000, 0]}
    epid = None
    while (True):
        try:
            algo_stats = get_algo_info()
            btc_price = get_btc_price()

            print_algos(algo_stats, btc_price)

            #out = subprocess.Popen('py delete.py', shell=True)
            #os.kill(out.pid, signal.SIGINT)

            sleep(60)
        except KeyboardInterrupt:
            print("Ending...")

            # Kill the running miner if program crashes
            if epid is not None:
                os.kill(epid, signal.SIGINT)

            exit(0)
