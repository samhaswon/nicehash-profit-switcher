import nicehash
# from time import sleep

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

def print_algo(name: str, algo_stats: dict, factor: float):
    print("Algo:          {}".format(name))
    print("Profitability: {}".format(algo_stats[name] * factor))


if __name__ == "__main__":
    """public_api = nicehash.public_api(host, True)

    algo_stats = public_api.get_multialgo_info()
    print(algo_stats)"""
    algo_stats = get_algo_info()
    #print(algo_stats['zelhash'])
    print_algo("kawpow", algo_stats, 32400000)
    print_algo("zelhash", algo_stats, 63)