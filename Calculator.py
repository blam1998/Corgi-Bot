from Athena import Queries
from config import AmuletPath,RingPath,EarringPath
#Percentage can be calculated as follows
#CurrThreshold = 100

#Case: 3 Perks
#Perk2Percentage/(currThreshold - Perk1ClassPercentage) * (Perk3Percentage/currThreshold - Perk2ClassPercentage) * (1/6)

#Case: 2 perks
#Perk2Percentage/(currThreshold - Perk1ClassPercentage)

#Note: currThreshold is updated after every (currThreshold - Perk#ClassPercentage)

#####1 Dictionaries####
#1 - {Perk:
#       {PerkClass:
#           {'PerkClassPercentage':float},
#           {'PerkPercentage': float}
#       }
#    }

###################
#ResultSet = Dict
#Rows = list
#Data = list
#Each data piece is a dictionary with key VarCharValue
#print(results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])
###################

class Calculator:
    def __init__(self):
        self.ringPerks = {}
        self.amuletPerks = {}
        self.earringPerks = {}
        self.globalPerks = {}

        self.generalPerkQuery("Amulet")
        self.generalPerkQuery("Ring")
        self.generalPerkQuery("Earring")

        """
        self.amuletPerkQuery()
        self.ringPerkQuery()
        self.earringPerkQuery()
        """

    def generalPerkQuery(self,accessoryType):
        match accessoryType:
            case "Amulet":
                tempDict = self.amuletPerks
                tableName = "amuletreader"
                path = AmuletPath
            case "Ring":
                tempDict = self.ringPerks
                tableName = "ringreader"
                path = RingPath
            case "Earring":
                tempDict = self.earringPerks
                tableName = "earringreader"
                path = EarringPath
            case default:
                return 0

        dict = Queries('SELECT percentage,perkname,perkclass FROM ' + tableName + " WHERE percentage IS NOT NULL", path)
        assert(len(dict['ResultSet']['Rows']) > 0)
        temp = []
        perkClass = {}

        for i in range(1,len(dict['ResultSet']['Rows'])):
            temp.clear()
            #print('========')
            for j in range(len(dict['ResultSet']['Rows'][i].get('Data'))):
                value = dict['ResultSet']['Rows'][i]['Data'][j]['VarCharValue']
                temp.append(value)
                #print(value)

            percentage = float(temp[0])
            perkName = temp[1].lower()
            perkClassName = temp[2]

            tempDict[perkName] = {}
            tempDict[perkName][perkClassName] = {}
            tempDict[perkName][perkClassName]['PerkClassPercentage'] = 1.0
            tempDict[perkName][perkClassName]['PerkPercentage'] = percentage
            self.globalPerks[perkName] = perkClassName

            if perkClassName not in perkClass:
                perkClass[perkClassName] = percentage
            else:
                perkClass[perkClassName] += percentage

        #i = Perk Name
        for i in tempDict:
            #j = PerkClassName
            for j in tempDict.get(i):
                tempDict.get(i).get(j)['PerkClassPercentage'] = perkClass.get(j)

    async def craft(self,args):
        currThreshold = 100.0
        perks = []

        temp = args[0]
        accessoryOption = temp.lower()
        #print(accessoryOption)
        #Error Cases#
        #Matching perkClass [O] -5
        #accessory typo [O] -3
        #perk name typo or does not exist in accessory class[O] -1
        #has more than 3 perks [O] -2
        #has less than 2 perks or command invalid [O] -4

        if len(args) < 3:
            print(len(args))
            print(args)
            return -4

        for i in range(1,len(args)):
            perks.append(args[i].lower())


        for i in range(len(perks)):
            j = len(perks) - 1
            while j > i:
                if self.globalPerks.get(perks[i]) == self.globalPerks.get(perks[j]):
                    print("Duplicate Perk Class Error")
                    return -5
                j -= 1

        if accessoryOption == 'amulet':
            accessoryPerks = self.amuletPerks
        elif accessoryOption == 'ring':
            accessoryPerks = self.ringPerks
        elif accessoryOption == 'earring':
            accessoryPerks = self.earringPerks
        else:
            print("Accessory Option Didn't match")
            return -3

        for k in perks:
            if k not in accessoryPerks:
                print("Failed: {}".format(k))
                return -1

        #Always Execute
        perk2ClassName = self.globalPerks[perks[1]]
        perk2Percentage = accessoryPerks.get(perks[1]).get(perk2ClassName).get('PerkPercentage')
        perk1ClassName = self.globalPerks[perks[0]]
        perk1ClassPercentage = accessoryPerks.get(perks[0]).get(perk1ClassName).get('PerkClassPercentage')


        #Case: 2 Perks
        #Perk2Percentage/(currThreshold - Perk1ClassPercentage)
        if len(perks) == 2:
            print((perk2Percentage/(currThreshold - perk1ClassPercentage)) * 100)
            return (perk2Percentage/(currThreshold - perk1ClassPercentage)) * 100

        #Case: 3 Perks
        #Perk2Percentage/(currThreshold - Perk1ClassPercentage) * (Perk3Percentage/currThreshold - Perk2ClassPercentage) * (1/6)
        elif len(perks) == 3:
            perk2ClassPercentage = accessoryPerks.get(perks[1]).get(perk2ClassName).get('PerkClassPercentage')
            perk3ClassName = self.globalPerks.get(perks[2])
            perk3Percentage = accessoryPerks.get(perks[2]).get(perk3ClassName).get('PerkPercentage')

            result = perk2Percentage/(currThreshold - perk1ClassPercentage)
            currThreshold -= perk1ClassPercentage
            return (result * (perk3Percentage/(currThreshold - perk2ClassPercentage)) * (1/6)) * 100
        else:
            return -2

