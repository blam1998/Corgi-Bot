import discord
from discord.ext import commands
from Athena import Queries
import random
from config import GamblePath
from Calculator import Calculator


client = commands.Bot(command_prefix = '!')
random.seed(version=2)
AccessoryCraft = Calculator()

#ResultSet = Dict
#Rows = list
#Data = list
#Each data piece is a dictionary with key VarCharValue
#print(results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])

class Gamble(commands.Cog):
    def __init__(self,bot):
        self.bot = bot;


    #Bot returns what user type, test command
    @client.command()
    async def ret(self,ctx,arg):
        await ctx.send(arg)

    async def coinsUpdate(self,userId,coins):
        Queries('update yeniry set username = \'{}\', coins = \'{}\' where username = \'{}\''.format(userId,coins,userId),GamblePath)

    @client.command()
    async def craft(self,ctx,*args):
        tempString = ""
        tempList = []

        for i in range(len(args)):
            detuple = args[i]
            if detuple != '|':
                tempString += detuple + ' '
            elif detuple == '|':
                tempList.append(tempString)
                tempString = ""

        tempList.append(tempString)

        for i in range(len(tempList)):
            tempList[i] = tempList[i].strip()

        async def errorNumber(ctx,result,args):
            match result:
                case -1:
                    await ctx.send("Please check your spelling or perk name.\n" + "Craft Help: !craft accessory_type | base_perk | perk2 | perk3")
                case -2:
                    await ctx.send("Accessories can only have 3 perks, each perk is separated by spaces.\n" + "Craft Help: !craft accessory_type | base_perk | perk2 | perk3")
                case -3:
                    await ctx.send("{} is invalid.\n".format(args[0]) + "Craft Help: !craft accessory_type | base_perk | perk2 | perk3")
                case -4:
                    await ctx.send("Each craft needs at least 2 perks and correct spelling of perk name.\n" + + "Craft Help: !craft accessory_type | base_perk | perk2 | perk3")
                case -5:
                    await ctx.send("You have duplicate perk class. Example: Refreshing and Refreshing Evasion\n" + "Craft Help: !craft accessory_type | base_perk | perk2 | perk3")
                case _:
                    if len(args) == 4:
                        await ctx.send("You have a {:.2f}% chance to craft a: [{} | {} | {}] {}.".format(result,args[1],args[2],args[3],args[0]))
                    else:
                        await ctx.send("You have a {:.2f}% chance to craft a: [{} | {}] {}.".format(result,args[1],args[2],args[0]))

        result = await AccessoryCraft.craft(tempList)
        await errorNumber(ctx,result,tempList)

    #Output users coins
    #If user is not registered in gambling, Add user id to SQL.
    #Else return user's coins
    @client.command()
    async def Coins(self,ctx):
        userId = ctx.author.id

        dict = Queries('SELECT coins FROM yeniry WHERE username = \'{}\''.format(userId),GamblePath)
        coins = dict['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']
        await ctx.send(coins)

    #!roulette color coins
    #green = 2x | blue = 4x | red = 8x
    @client.command()
    async def roulette(self,ctx,*args):
        dict = Queries('SELECT coins FROM yeniry WHERE username = \'{}\''.format(ctx.author.id),GamblePath)
        coins = dict['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']
        color = args[0].lower()

        coins = int(coins)

        if coins < int(args[1]):
            await ctx.send("You only have {} coins".format(coins))
        else:
            roll = random.randrange(0,1000,1)
            if color == "green" and (roll < 525 and roll >= 0):
                coins += int(args[1]) * 2
                await ctx.send("You won, your coin balance is: {}".format(int(coins) + int(args[1])))
                await self.coinsUpdate(ctx.author.id, coins)
            elif color == "red" and (roll >= 525 and roll < 700):
                coins += int(args[1]) * 8
                await ctx.send("You won, your coin balance is: {}".format(coins))
                await self.coinsUpdate(ctx.author.id, coins)
            elif color == "blue" and (roll >= 700 and roll < 1000):
                coins += int(args[1]) * 4
                await ctx.send("You won, your coin balance is: {}".format(coins))
                await self.coinsUpdate(ctx.author.id, coins)
            else:
                await ctx.send("You lost, your coin balance is: {}".format(int(coins) - int(args[1])))
                await self.coinsUpdate(ctx.author.id,int(coins) - int(args[1]))


    @client.command()
    async def coinprint(self,ctx,arg):
        print(ctx.author.id)
        print(arg)
        Queries('INSERT INTO yeniry VALUES (\'{}\',\'{}\')'.format(ctx.author.id,arg),GamblePath)

    @client.command()
    async def update(self,ctx,arg):
        Queries('update yeniry set username = \'{}\', coins = \'{}\' where username = \'{}\''.format(ctx.author.id,arg,ctx.author.id),GamblePath)

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.content.startswith("hello"):
            #message.author --> discord name
            print(message.author.id)
            await message.channel.send("Cyka")

    @commands.Cog.listener()
    async def on_ready(self):
        print("yeniry is awake")

def setup(client):
    client.add_cog(Gamble(client));
