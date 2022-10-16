from switch import Switch_Info, Switch_Thread
from time import sleep


def main():
    try:
        # Setup algos + switch
        # algos format: "name_of_algo": [speed, pay (set to 0)]
        algos = {"kawpow": [32400000, 0], 
                "zelhash": [63, 0], 
                "daggerhashimoto": [71500000, 0], 
                "autolykos": [165500000, 0],
                "etchash": [71500000, 0]}
        # commands format: "name_of_algo": "command"
        commands = {"kawpow": "delete.py", 
                    "zelhash": "delete.py",
                    "daggerhashimoto": "delete.py", 
                    "autolykos": "delete.py", 
                    "etchash": "delete.py"}
        host = 'https://api2.nicehash.com'
        algo_switch = Switch_Info(host, 1, algos)
        mining_switch = Switch_Thread(commands, 'python3')

        while True:
            current_algo_to_mine = algo_switch.algo_to_mine()
            mining_switch.set_current(current_algo_to_mine)
            sleep(60)

    except KeyboardInterrupt:
        exit(0)

if __name__ == '__main__':
    main()
