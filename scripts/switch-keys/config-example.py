### this is very experimental code, it has barely been tested and I don't really even know what I am doing.
### Use it with caution and at your own risk.  It seriously might not work right.
### It will kill any running instance of witness_node and relaunch witness_node in a new screen named witness
### there is a delay between launching the witness_node and launching the cli_wallet.  This is to give your witness node enough time to open up and get ready to accept the connection
### from your cli_wallet.  It is currently set to 3 minutes for a --replay and 5 minutes for a --resync.  You can modify these wait times on lines 27 and 82 of switch.py

# the name of your witness as string
witnessname = "test.dele-puppy"

# witness number
witness_object = "1.6.13"
# the password of your wallet as string
wallet_password = "puppiesRkewl" # not really my password.  Just left in so people can see how it should look.

# the public keys you would like to switch between must have at least two.  Can list the same key twice if needed
publickeys = ("BTS69EvfYBsXJDAusZW8Aci2frFqPdcSCcEpUXq4kbtnvQ9V3mtRa","BTS8cvopYL8Y6US6dXdFGRjJssVFvA9Fr4WiYtgnqn37WDVj87deT")

# How many missed blocks to wait for until switching to new key.
# very little testing has been done with any value other than 1
strictness = 1

# public keys you would like to use in case of emergency.  Set to 0 if you do not want to use emergency keys.
# if keys are used, must enter at least two.  Can list the same key twice if needed.
emergencykeys = 0

# the full path to your witness_node binary including binary name
path_to_witness_node = "/home/user/src/bitshares-2/programs/witness_node/witness_node"

# The full path to your data directory
path_to_data_dir = "/home/user/src/bitshares-2/programs/witness_node/witness_node_data_dir"

# rpc host and port
rpc_port = "127.0.0.1:8092"

# the full path too your cli_wallet binary including binary
path_to_cli_wallet = "/home/user/src/bitshares-2/programs/cli_wallet/cli_wallet"

# the full path to your wallet json including json file.
path_to_wallet_json = "/home/user/src/bitshares-2/programs/cli_wallet/wallet.json"


path_to_feed_script = "/home/user/src/python-graphenelib/scripts/pricefeeds/pricefeeds.py"

# minute that will trigger feed script.  This needs to be less than the feed_script_interval or feed script will never trigger
feed_script_trigger = 1

# number of minutes between triggering the feed script
feed_script_interval = 10

# if set to true script will try to trigger the pricefeed script.  If set to false then password, wallet.json path,
# feed script path, interval, and trigger are not needed.
feed_script_active = False

# determines whether or not switch.py will attempt to switch keys when a block is missed.  It will attempt to switch keys no matter what if your remote nodes
# return two different signing keys.  This has not yet been tested with false.
switching_active = True
