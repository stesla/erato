import random

from discord.ext import commands
from functools import reduce

class Context(commands.Context):
    def roll(self, ndice, nsides):
        dice = [random.choice(range(1, nsides + 1)) for _ in range(ndice)]
        sum = reduce(lambda a, b: a + b, dice)
        return ' + '.join(map(lambda d: str(d), dice)) + ' = ' + str(sum)

class Bot(commands.Bot):
    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)


