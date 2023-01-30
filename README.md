# nicehash-profit-switcher
Just a simple program to query NiceHash's api and switch external miners based on the current profit situation. It is primarily designed to be used with external scripts for individual algo overclocking, but could be adapted to be used in other ways.

**Requires Python 3**, developed using version *3.10.6*

## Setup
To setup the program, open main.py to edit two dictionaries: algos and commands.

### Algos
For algos, enter the name of an algo from Nicehash in all lower case letters along with your speed with no prefixes (H/Sol/G) ending with a 0. It should follow the format: "name_of_algo": [speed, pay (set to 0), power in kW] for each algorithm. Note, power is the instant consumption and not the daily consumption which would be kWh. 

### Commands
For commands, enter the name of an algo from Nicehash in all lower case letters followed by your launch script name. As for launching it, the method must be specified below in the initilization command of mining_switch. The default I put in there for testing it is ```'bash'```, but just replace it with ```'./'``` or ```'.\'``` or whatever you need to run your scripts. You can also change the switch interval in the algo_switch initilization command. It is the integer in the middle.

Good luck and happy mining!
