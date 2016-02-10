import bot

# Load the configuration
import config

if __name__ == '__main__':

    # initialize the bot infrastructure with our settings
    bot.init(config)

    # execute the bot(s) continuously and get notified via websocket
    bot.execute()
