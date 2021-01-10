import discord
from discord.ext import commands
import sys
import logging
import datetime
from PIL import Image, ImageDraw
import os
import re
from cd import CD
from cdError import CDError
from draw import Draw

INVITE_LINK = "https://discord.com/api/oauth2/authorize?client_id=795909275880259604&permissions=34816&scope=bot"
TOKEN = open("../txt/TOKEN.txt", "r").read()
PREFIX = open("../txt/PREFIX.txt", "r").read()

client = commands.Bot(command_prefix = PREFIX)

# Runs on client ready.
@client.event
async def on_ready():
    await client.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            type = discord.ActivityType.watching,
            name = PREFIX + "help"
        )
    )

    a_logger.info("INFO: Bot is ready.")
    a_logger.info(f"INFO: Prefix is {PREFIX}")

# Shows a Coxeter-Dynkin diagram.
@client.command()
async def cd(ctx, *cd):
    cd = ' '.join(cd)
    a_logger.info(f"COMMAND: cd {cd}.")

    if cd == '':
        await ctx.send(f"Usage: `{PREFIX}cd x4o3o`. Run `{PREFIX}help cd` for details.")
    elif cd == 'c': # Dumb easter egg.
        await ctx.send("https://www.cdc.gov/")
    elif cd == 'play': # Another dumb easter egg.
        await ctx.send(":cd: :play_pause:")
    elif cd == 'pause': # Another dumb easter egg.
        await ctx.send(":cd: :pause_button:")
    else:
        try:
            temp = Draw(CD(cd).toGraph()).draw()
        except CDError as e:
            await error(ctx, e, expected = True)
            return
        except Exception as e:
            await error(ctx, e, expected = False)
            return

    temp.save("temp.png")
    a_logger.info(f"INFO: Created temp.png file.")
    await ctx.send(file = discord.File("temp.png"))
    os.remove("temp.png")
    a_logger.info(f"INFO: Removed temp.png file.")

# Shows a help screen with a command list.
client.remove_command("help")
@client.command(pass_context = True)
async def help(ctx):
    await ctx.send(embed = helpEmbed)
    a_logger.info("COMMAND: help")

# Gets the bot invite link.
@client.command()
async def invite(ctx):
    a_logger.info("COMMAND: invite")
    await ctx.send(INVITE_LINK)

# Dev command, shows the client latency.
@client.command()
async def ping(ctx):
    a_logger.info(f"COMMAND: ping")

    latency = round(client.latency * 1000)
    a_logger.info(f"INFO: Latency {latency}ms.")
    await ctx.send(f"Ping: {latency}ms.")

# Changes the bot prefix.
@commands.has_permissions(administrator = True)
@client.command()
async def prefix(ctx, *newPrefix):
    newPrefix = ' '.join(newPrefix)
    a_logger.info(f"COMMAND: prefix {newPrefix}")

    PREFIX = newPrefix
    client.command_prefix = PREFIX
    open("PREFIX.TXT", "w").write(PREFIX)

    a_logger.info(f"INFO: prefix changed to {newPrefix}")
    await ctx.send(f"Prefix changed to {PREFIX}")

# Logs an error and posts it.
async def error(ctx, e, expected):
    if expected:
        expectedStr = ""
    else:
        expectedStr = "UNEXPECTED "

    a_logger.info(f"{expectedStr}ERROR: {str(e)}")
    await ctx.send(f"`{expectedStr}ERROR: {str(e)}`")

# Configures logger.
a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)
output_file_handler = logging.FileHandler("../../logs/log " +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt")
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)

# Configures help embed.
helpEmbed = discord.Embed(
    colour = discord.Colour.blue()
)

helpEmbed.set_author(name = "Coxeter Bot Help")
helpEmbed.add_field(name = f"`{PREFIX}help`", value = "You said this.", inline = False)
helpEmbed.add_field(name = f"`{PREFIX}cd [linearized diagram]`",
    value = ("Renders a Coxeter–Dynkin Diagram, based on [Richard Klitzing's notation]"
    "(https://bendwavy.org/klitzing/explain/dynkin-notation.htm).\n"
    "URL and/or Cirro still have to code this."), inline = False)

# Runs the bot.
client.run(TOKEN)
