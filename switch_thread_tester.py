from switch import Switch_Thread
from time import sleep

if __name__ == '__main__':
    try:
        commands = {"kawpow": "delete.py", 
                    "zelhash": "delete.py",
                    "daggerhashimoto": "delete.py", 
                    "autolykos": "delete.py", 
                    "etchash": "delete.py"}
        swtch_thrd_test = Switch_Thread(commands, 'python3')

        for key in commands:
            print("Running {}".format(key))
            swtch_thrd_test.set_current(key)
            sleep(10)

        print("Done")
    except KeyboardInterrupt:
        print("Ending...")
        exit(0)