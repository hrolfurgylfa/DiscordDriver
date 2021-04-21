# Standard
import os

# Community
from discord.ext import commands
from discord_slash import SlashCommand

# Custom
from Settings import keys


######################
#  Global Variables  #
######################

# Create bot
bot = commands.Bot(command_prefix="prefix")
slash = SlashCommand(
    bot,
    delete_from_unused_guilds=True,
    override_type=True,
    sync_commands=True,
    sync_on_cog_reload=True,
)


####################
#  Discord Events  #
####################


@bot.event
async def on_ready():
    print("Starting!")


##################
#  Load Modules  #
##################

command_dir = "Commands"
directory = os.fsencode(command_dir)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".py"):
        bot.load_extension(f"{command_dir}.{filename[0:-3]}")


###############
#  Start Bot  #
###############

bot.run(keys.DISCORD_TOKEN)
