
# the password of your wallet as string
wallet_password = "puppiesRkewl" # not really my password.  Just left in so people can see how it should look.

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

# full path to xerocs feed script.  Script needs to be modified to not require confirmation.
path_to_feed_script = "/home/user/src/python-graphenelib/scripts/pricefeeds/pricefeeds.py"

# minute that will trigger feed script.  This needs to be less than the feed_script_interval or feed script will never trigger
feed_script_trigger = 1

# number of minutes between triggering the feed script
feed_script_interval = 10

# if set to true script will try to trigger the pricefeed script.  If set to false then password, wallet.json path,
# feed script path, interval, and trigger are not needed.
feed_script_active = True

