import random
import logging

from discord.ext import commands
from functools import reduce

from .model import *

logger = logging.getLogger(__name__)

STATS = ('daring', 'grace', 'heart', 'wit', 'spirit')

class CharacterExists(Exception):
    pass

class Context(commands.Context):
    @property
    def character(self):
        return Character.lookup(self.message.author.id, self.guild.id)

    @db.atomic()
    def create_character(self):
       try:
            self.character
            raise CharacterExists()
       except Character.DoesNotExist:
            char = Character(user_id=self.message.author.id, guild_id=self.guild.id)
            char.save()

    @db.atomic()
    def give_string(self, member):
        owner = Character.lookup(member.id, self.guild.id)
        target = Character.lookup(self.message.author.id, self.guild.id)
        string = String(owner=owner, target=target)
        string.save()
        return len(owner.strings.where(String.target == target))

    @db.atomic()
    def list_strings(self, member):
        owner = Character.lookup(member.id, self.guild.id)
        query = (Character
                .select(Character.user_id, fn.COUNT(String.target_id).alias('count'))
                .join(String, on=String.target)
                .where(String.owner == owner)
                .group_by(Character.user_id))
        for row in query:
            member = self.guild.get_member(row.user_id)
            yield (member, row.count)


    def roll(self, stat, modifier):
        ndice, nsides = 6, 2
        dice = [random.choice(range(1, nsides + 1)) for _ in range(ndice)]
        sum = reduce(lambda a, b: a + b, dice)
        if stat is not None:
            char = self.character
            sum += getattr(self.character, stat)
        if modifier is not None:
            sum += modifier
        if sum >= 10:
            return f'Up Beat ({sum})'
        elif sum >= 7:
            return f'Mixed Beat ({sum})'
        else:
            return f'Down Beat ({sum})'

    def list_stats(self, user):
       char = Character.lookup(user.id, self.guild.id)
       for s in STATS:
           yield (s, getattr(char, s))

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

def valid_stat(argument):
    lowered = argument.lower()
    if lowered in STATS:
        return lowered
    else:
        raise Invalid('Stat', STATS)
