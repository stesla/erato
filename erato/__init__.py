import random
import logging

from discord.ext import commands
from functools import reduce

from .model import db, Character

logger = logging.getLogger(__name__)

TRAITS = ('daring', 'grace', 'heart', 'wit', 'spirit')

class CharacterExists(Exception):
    pass

class Context(commands.Context):
    @property
    def character(self):
        return Character.get((Character.user_id == self.message.author.id) &
                             (Character.guild_id == self.guild.id))

    @db.atomic()
    def create_character(self):
       try:
            self.character
            raise CharacterExists()
       except Character.DoesNotExist:
            char = Character(user_id=self.message.author.id, guild_id=self.guild.id)
            char.save()

    def roll(self, trait, modifier):
        ndice, nsides = 6, 2
        dice = [random.choice(range(1, nsides + 1)) for _ in range(ndice)]
        char = self.character
        sum = reduce(lambda a, b: a + b, dice)
        sum += getattr(self.character, trait)
        sum += modifier
        if sum >= 10:
            return f'Up Beat ({sum})'
        elif sum >= 7:
            return f'Mixed Beat ({sum})'
        else:
            return f'Down Beat ({sum})'


    @db.atomic()
    def set_character_attribute(self, stat, value):
        char = self.character
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
    def __init__(self, typ, values):
        self.typ = typ
        self.values = ', '.join(values)

    def __str__(self):
        return f'{self.typ} must be one of: {self.values}.'

def valid_trait(argument):
    lowered = argument.lower()
    if lowered in TRAITS:
        return lowered
    else:
        raise Invalid('Trait', TRAITS)
