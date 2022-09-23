import nicehash
# import os
import subprocess
from time import sleep

host = 'https://api2.nicehash.com'
#host = 'https://api-test.nicehash.com'


def response_parse(response):
    return {algorithm['algorithm'].lower(): float(algorithm['paying'])
            for algorithm in response['miningAlgorithms']}

def get_algo_info():
    # api query
    public_api = nicehash.public_api(host, False)
    algo_stats = public_api.get_multialgo_info()

    # Parse response to dictionary
    algos = response_parse(algo_stats)
    return algos

def print_algo(name: str, factor: float, algo_stats: dict):
    print("Algo:          {}".format(name))
    print("Profitability: {}".format(int(algo_stats[name] * factor)))


if __name__ == "__main__":
    while (True):
        algo_stats = get_algo_info()
        print_algo("kawpow", 32400000, algo_stats)
        print_algo("zelhash", 63, algo_stats)

        subprocess.run(["echo", "Running"])
        sleep(60)
