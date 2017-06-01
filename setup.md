# Sovrin Client

Sovrin Client to interact with Sovrin Network (public/permissioned distributed ledger)

### Setup Instructions

#### Run common setup instructions
Follow instructions mentioned here [Common Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

Follow instructions mentioned here [Charm-Crypto Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

### Run tests [Optional]

Note: The tests create Sovrin nodes (dont worry, all nodes are created in the same process) . 

To run the tests, download the source by cloning this repo. 
Navigate to the root directory of the source and install required packages by
```
pip install -e .
```

Run test by 
```
python setup.py pytest
```


### Installing Sovrin client
```
pip install -U --no-cache-dir sovrin-client
```

Note. The tests create Sovrin nodes (dont worry, all nodes are created in the same process).

#### Configuration


### Start Sovrin client CLI (command line interface)
Once installed, you can play with the command-line interface by running Sovrin from a terminal.

Note: For Windows, we recommended using either [cmder](http://cmder.net/) or [conemu](https://conemu.github.io/).
```
sovrin
```
