from tortoise.models import Model
from tortoise import fields


class Users(Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=255)
    rating = fields.FloatField(default=0.0)
    wins = fields.IntField(default=0)
    losses = fields.IntField(default=0)


class Game(Model):
    id = fields.IntField(pk=True)
    player1 = fields.ForeignKeyField('models.Users', related_name='player1_games')
    player2 = fields.ForeignKeyField('models.Users', related_name='player2_games', null=True)
    status = fields.CharField(max_length=20, default='waiting')  # statuses: waiting, ongoing, finished
    player1_points = fields.IntField(default=0)
    player2_points = fields.IntField(default=0)
    win = fields.ForeignKeyField('models.Users', related_name='win_games', null=True)