import os
import yaml

from peewee import *

db = SqliteDatabase(os.getenv('DATABASE', 'erato.sqlite3'))

class BaseModel(Model):
    class Meta:
        database = db

class Character(BaseModel):
    class Meta:
        table_name = 'characters'

    # identifiers
    user_id = BigIntegerField()
    guild_id = BigIntegerField()
    
    # stats
    daring = IntegerField(default=0)
    grace = IntegerField(default=0)
    heart = IntegerField(default=0)
    wit = IntegerField(default=0)
    spirit = IntegerField(default=0)

    # other fields
    xp = IntegerField(default=0)

    @classmethod
    def lookup(cls, user_id, guild_id):
        return cls.get((cls.user_id == user_id) & (cls.guild_id == guild_id))

Character.add_index(Character.user_id, Character.guild_id, unique=True)

class MovesDatabase:
    def __init__(self, filename):
        with open(filename) as f:
            self.data = yaml.load(f, Loader=yaml.FullLoader)

    @property
    def moves(self):
        return self.data

movesdb = MovesDatabase(os.getenv('MOVES', 'erato-moves.yaml'))

class String(BaseModel):
    class Meta:
        table_name = 'strings'

    owner = ForeignKeyField(Character, backref='strings')
    target = ForeignKeyField(Character)

def initialize():
    db.connect()
    db.create_tables([Character, String])
