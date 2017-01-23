# Sovrin Client

Sovrin Client to interact with Sovrin Network (public/permissioned distributed ledger)

### Setup Instructions

#### Run common setup instructions
Follow instructions mentioned here [Common Setup Instructions](https://github.com/sovrin-foundation/sovrin-common/blob/master/setup.md)

#### Setup Charm-Crypto

Sovrin-client requires anonymous credentials library which requires a cryptographic library.
The default configuration includes an example that uses Charm-Crypto framework.
The steps to install charm-crypto are mentioned in our [Anonymous Credentials](https://github.com/evernym/anoncreds) repository. 
You just have to run `setup-charm.sh` script. It will require sudo privileges on the system.

## Installing Sovrin client
```
pip install sovrin-client
```

Or to run the tests too, download this source by cloning this repo. Navigate to the root directory of the source and install Sovrin by    
```
pip install -e .
```

### Run tests [Optional]
Run the tests (if you have downloaded the source). 

```
python -m sovrin_client.test
```
Note. The tests create Sovrin nodes (dont worry, all nodes are created in the same process) which require OrientDB to be running. You can install OrientDB from [here](https://github.com/evernym/sovrin-common/blob/master/orientdb_installation.md).


### Configuration
A Sovrin client can be configured to use flat files or OrientDB for persistence. To use files instead of OrientDB you need to add 2 entries 
in your configuration located at `~/.sovrin/sovrin_config.py`.
<br>The first entry to add is
```
ClientIdentityGraph = False
```

And the second is
```
ReqReplyStore = "file"
```

### Start Sovrin client CLI (command line interface)
Once installed, you can play with the command-line interface by running Sovrin from a terminal.

Note: For Windows, we recommended using either [cmder](http://cmder.net/) or [conemu](https://conemu.github.io/).

```
sovrin
```