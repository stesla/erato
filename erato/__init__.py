import random
import logging

from discord.ext import commands
from functools import reduce

from .model import db, Character

logger = logging.getLogger(__name__)

TRAITS = ('daring', 'grace', 'heart', 'wit', 'spirit')
CONDITIONS = ('angry', 'frightened', 'guilty', 'hopeless', 'insecure')

class CharacterExists(Exception):
    pass

class Context(commands.Context):
    @db.atomic()
    def create_character(self):
        user_id = self.message.author.id
        guild_id = self.guild.id
        try:
            Character.get(
                (Character.user_id == user_id) &
                (Character.guild_id == guild_id))
            raise CharacterExists()
        except Character.DoesNotExist:
            char = Character(user_id=user_id, guild_id=guild_id)
            char.save()

    def roll(self, ndice, nsides):
        dice = [random.choice(range(1, nsides + 1)) for _ in range(ndice)]
        sum = reduce(lambda a, b: a + b, dice)
        return ' + '.join(map(lambda d: str(d), dice)) + ' = ' + str(sum)

    @db.atomic()
    def set_character_attribute(self, stat, value):
        user_id = self.message.author.id
        guild_id = self.guild.id
        char = Character.get(
            (Character.user_id == user_id) &
            (Character.guild_id == guild_id))
        setattr(char, stat, value)
        char.save()

class Bot(commands.Bot):
    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)
        else:
            await super().on_command_error(ctx, error)

class Invalid(Exception):
    pass

def valid(valid_values):
    def f(argument):
        lowered = argument.lower()
        if lowered in valid_values:
            return lowered
        else:
            raise Invalid()
    return f
