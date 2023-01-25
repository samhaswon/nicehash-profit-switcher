from switch import Switch_Info, Switch_Thread
from time import sleep


if __name__ == "__main__":
    # Setup algos + switch
    # algos format: "name_of_algo": [speed, pay (set to 0), power in kW]
    algos = {"kawpow": [33190000, 0, 0.208], 
            "Kawpow": [31350000, 0, 0.187],
            "zelhash": [63, 0, 0.170], 
            "daggerhashimoto": [71500000, 0, 0.180], 
            "autolykos": [165500000, 0, 0.220],
            "etchash": [71500000, 0, 0.180],
            "kheavyhash": [709000000, 0, 0.249]}
    # commands format: "name_of_algo": "command"
    commands = {"kawpow": "minervn.sh",
                "Kawpow": "minervn_e.sh", 
                "zelhash": "minezel.sh",
                "daggerhashimoto": "mineeth.sh", 
                "autolykos": "mineergo.sh", 
                "etchash": "mineetc.sh",
                "kheavyhash": "minekaspa.sh"}
    host = 'https://api2.nicehash.com'
    algo_switch = Switch_Info(host, 1, algos, 20, 0.10242)
    mining_switch = Switch_Thread(commands, 'bash')
    mining = False

    while True:
        try:
            current_algo_to_mine = algo_switch.algo_to_mine()
            # Minimum profit (in Satoshi)
            if current_algo_to_mine[1] > -250:
                mining_switch.set_current(current_algo_to_mine[0])
                mining = True
            elif mining:
                mining = False
                mining_switch.stop()
                mining_switch.set_current("")

        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)

        except Exception as ex:
            print("Error: {}".format(ex))
            exit(1)

        else:
            sleep(60)
