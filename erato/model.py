import os

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

Character.add_index(Character.user_id, Character.guild_id, unique=True)

def initialize():
    db.connect()
    db.create_tables([Character])
