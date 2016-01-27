from bot import Bot

# Load the configuration
import config

if __name__ == '__main__':

    # initialize the bot infrastructure with our settings
    bot = Bot(config)

    # execute the bot(s) just once
    bot.execute()
