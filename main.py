"""
WikiWally Discord Bot

WikiWally is a bot that allows Discord users to request specific or random 
articles from Wikipedia, which are then displayed as embeds in the channel 
where the bot command was executed.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from mediawiki import MediaWiki, DisambiguationError
wikipedia = MediaWiki()
import random

# Bot Setup
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents().all()
client = discord.Client(intent=intents)
bot = commands.Bot(command_prefix=".",intents=intents)

# Notify when the bot is connected to Discord.
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


# WikiWally Bot Commands
@bot.group(help="Commands for WikiWally")
async def wiki(ctx):
    """ Initializes "wiki" master command for bot.
    This was done to make it easier for users to distinguish 
    commands for different bots in a server given the same command prefix.
    """
    if ctx.invoked_subcommand is None:
        await ctx.channel.send("Invalid wiki command passed...")

# WikiWally Subcommands
@wiki.command(name="page", help="Fetches an article given user input")
async def get_page(ctx, *, user_input):
    """ Returns a Wikipedia page that most closely matches the user"s input.
    The Wikipedia page is provided to the user in the form of an embed 
    containing the page"s title, url, a two-sentence description, an image 
    from the page (if applicable), and the Discord user who made the request.
    """

    try:
        # Get the first result from a list of articles 
        # associated with the user_input.
        query = wikipedia.search(user_input)[0]

        # Get the Wikipedia page from the given query.
        # auto_suggest is set to False because, when set to True, the "page" 
        # method sometimes sends a PageError even if a page matching the 
        # query exists.
        page = wikipedia.page(query, auto_suggest=False)

        embed = discord.Embed(
            title = page.title, 
            url = page.url,
            description = wikipedia.summary(query, sentences=2, auto_suggest=False), 
            color= 0xFAD02C
            )

        # Get a thumbnail image from the Wikipedia article for the embed.
        img_all = page.images

        # Filter out SVG images as they don't work with Discord's embed.
        img_list = [img for img in img_all if img[len(img)-3:] != 'svg']
        
        # Using the second image in "img_all" seems to give the main
        # image of the article more consistently than the first element.
        if len(img_list) == 1:
            embed.set_image(url=img_list[0])

        elif len(img_list) > 1:
            embed.set_image(url=img_list[1])

    except IndexError:
        # This occurs when a Wikipedia page cannot be found given the user input.
        # The actual error thrown is IndexError, however this results from a PageError:
        # Because user inputs are being susbtituted with the first query from 
        # wikipedia.search(user_input), an IndexError is thrown if no pages for 
        # that user_input can be found.

        page_err_msg = "The page you are looking for might not exist. Please try a different query!"

        embed = discord.Embed(
            title="Page Error", 
            description = page_err_msg, 
            color= 0xFAD02C
            )

    except DisambiguationError as dis_err:
        # This error occurs when multiple Wikipedia pages are found for a given query.

        dis_err_msg = "Disambiguation Error: There may be multiple entries for your query." 

        dis_options = dis_err.options

        # This check is done to prevent exceeding embed's field limits.
        if len(dis_err.options) > 20:
            dis_options = dis_options[:19]

        # Gives each option its own line in the embed.
        dis_options = "\n".join(dis_options)

        embed = discord.Embed(
                title= dis_err_msg,
                description = "Query inputted: {}".format(query), 
                color= 0xFAD02C
                )

        embed.add_field(name="Possible entries: ", value=dis_options)
        
    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    await ctx.channel.send(embed=embed)


@wiki.command(name="random", help="Fetches a random Wikipedia article. An integer from 1 to 10 can also be entered for a list of 1 to 10 random Wikipedia articles (e.g. *.wiki random 10)*.")
async def get_random_page(ctx, user_input=None):
    """Fetches 1 to 10 random articles for the user.
    user_input is a string that is then converted into an integer value.
    If an integer from 1 to 10 is not entered, a ValueError or TypeError is 
    thrown and the user is asked to input an appropriate value.
    """

    try:
        # If no integer is entered, the bot defaults to 1.
        if (user_input == None):
            user_input = 1

        else:
            user_input = int(user_input)
        
        # A ValueError is thrown for inputs larger than 10 are not accepted 
        # to prevent exceeding the embed limits and to keep the article 
        # output reasonably presentable.
        if (user_input > 10):
            raise ValueError

        # If only one Wikipedia article is requested, it is placed in an 
        # embed similar to that of the "page" command.
        elif user_input == 1:
            page_random = wikipedia.random(pages=user_input)
            
            try:
                page = wikipedia.page(page_random, auto_suggest=False)

            # If a DisambiguationError is encountered, the bot randomly 
            # chooses from a list of possible options.
            except DisambiguationError as dis_err:
                s = random.choice(dis_err.options)
                page = wikipedia.page(s, auto_suggest=False)

            embed = discord.Embed(
                    title=page.title, 
                    url=page.url,
                    description = wikipedia.summary(page.title, sentences=2, auto_suggest=False), 
                    color= 0xFAD02C
                    )

            # TODO: Make get_image(page) function
            img_all = page.images

            img_list = [img for img in img_all if img[len(img)-3:] == 'jpg']
            
            if len(img_list) == 1:
                embed.set_image(url=img_list[0])
            
            elif len(img_list) > 1:
                embed.set_image(url=img_list[1])

        # Executed when more than one Wikipedia article is requested.
        # A list of articles on an embed are returned to the user.
        else:
            page_list = wikipedia.random(pages=user_input)
            
            embed = discord.Embed(
                title="I found some articles for you!",
                color=0xFAD02C
            )

            for index, query in enumerate(page_list):
                try:
                    page = wikipedia.page(query, auto_suggest=False)
                    
                    index_string = str(index+1)

                    page_title = page.title
                    hyperlink = page.url
                    embed.add_field(name="Article " + index_string, value="[{}]({})".format(page_title, hyperlink), inline=False)

                # If a DisambiguationError is encountered, the bot randomly 
                # chooses from a list of possible options.
                except DisambiguationError as err:
                    s = random.choice(err.options)
                    page = wikipedia.page(s, auto_suggest=False)

    # Thrown when the numerical input is not a valid integer.
    except ValueError:
        
        val_err_msg = "Please input an integer from 1 to 10. If no number is entered, I'll send one article by default."

        embed = discord.Embed(
                title= "The query \"{}\" is not a valid input.".format(user_input), 
                description = val_err_msg,
                color= 0xFAD02C
                )
    
    # Thrown when the input cannot be converted into an integer.
    except TypeError:
        type_err_msg = "Please input an integer from 1 to 10. If no number is entered, I'll send one article by default."
    
        embed = discord.Embed(
                title= "The query \"{}\" is not a valid integer.".format(user_input), 
                description = type_err_msg,
                color= 0xFAD02C
                )
    
    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    await ctx.channel.send(embed=embed)


@wiki.command(name="options", help="Look for query options/suggestions for a given input. This may be helpful if you can't find the article you're looking for using the *page* command.")
async def get_options(ctx, user_input):
    """Provides the user with possible articles associated with their input.
    This command is intended to help the user find alternative queries
    if their original input did not provide them with the article they
    expected.
    """

    # Results are limited to 20 to avoid exceeding the character limits 
    # of the embed field and to make the output presentable.
    opts = wikipedia.search(user_input, results=20)

    # Return the list of options in an embed
    if opts:
        opts = "\n".join(opts)

        embed = discord.Embed(
            title="Article Options",
            description = "Input: {}".format(user_input), 
            color= 0xFAD02C
            )

        embed.add_field(name="Possible entries: ", value=opts)

    # Triggers if there are no possible options for the user input
    else:
        page_err_msg = "Articles for your query might not exist. Please try a different query!"

        embed = discord.Embed(
            title="No options found.", 
            description = page_err_msg, 
            color= 0xFAD02C
            )

    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    await ctx.channel.send(embed=embed)

bot.remove_command("help")
@wiki.command(name="help", help = "Help page for WikiWally Bot")
async def get_help(ctx):
    """Returns the names and functions of WikiWally subcommands in an embed."""

    embed = discord.Embed(
            title="WikiWally Bot Commands",
            description = "To use WikiWally Commands, enter ***.wiki [command name]*** ", 
            color= 0xFAD02C
            )
    
    for c in wiki.commands:
        embed.add_field(name=c.name, value = c.help, inline=False)

    embed.set_footer(text="Requested by: {}".format(ctx.author.display_name))
    await ctx.channel.send(embed=embed)

# Run the bot!    
bot.run(TOKEN)