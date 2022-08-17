import discord
from discord.ext import commands

class Misc_commands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    #!slap Target (word) Reason(string)
    @commands.command()
    async def slap(self,ctx,*args):
        target = args[0]
        reason = " ".join(args[1:(len(args))])
        await ctx.send("{} Slapped {} because {}".format(ctx.author.name,target,reason))



def setup(client):
    client.add_cog(Misc_commands(client));