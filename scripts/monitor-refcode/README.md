# Monitor Faucet

This script monitors deposits and searches for referral codes of length 8 in the memo.
After that, it makes a API call to the faucet to reserve these funds for later use.

## Configuration

    cp config-example.py config.py
    # edit config.py

## Run

    python3 monitor.py
