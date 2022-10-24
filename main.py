from switch import Switch_Info, Switch_Thread
from time import sleep


if __name__ == "__main__":
    # Setup algos + switch
    # algos format: "name_of_algo": [speed, pay (set to 0)]
    algos = {"kawpow": [32400000, 0], 
            "zelhash": [63, 0], 
            "daggerhashimoto": [71500000, 0], 
            "autolykos": [165500000, 0],
            "etchash": [71500000, 0]}
    # commands format: "name_of_algo": "command"
    commands = {"kawpow": "minervn.sh", 
                "zelhash": "minezel.sh",
                "daggerhashimoto": "mineeth.sh", 
                "autolykos": "mineergo.sh", 
                "etchash": "mineetc.sh"}
    host = 'https://api2.nicehash.com'
    algo_switch = Switch_Info(host, 1, algos, 20)
    mining_switch = Switch_Thread(commands, 'bash')

    while True:
        try:
            current_algo_to_mine = algo_switch.algo_to_mine()
            mining_switch.set_current(current_algo_to_mine)
            sleep(60)

        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)

        except Exception as ex:
            print("Error: {}".format(ex))
            exit(1)
