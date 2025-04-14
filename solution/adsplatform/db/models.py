from adsplatform.schemas.clients import Gender
from adsplatform.schemas.campaigns import TargetingGender

from tortoise import Model, fields


class Clients(Model):
    id = fields.UUIDField(pk=True, null=False)
    login = fields.CharField(max_length=1024, unique=True, null=False)
    age = fields.IntField(null=False)
    location = fields.CharField(max_length=1024, null=False)
    gender: Gender = fields.CharEnumField(enum_type=Gender, null=False)

    scores: fields.ReverseRelation['MLScores']

    impressions: fields.ReverseRelation['CampaignImpressions']
    clicks: fields.ReverseRelation['CampaignClicks']


class Advertisers(Model):
    id = fields.UUIDField(pk=True, null=False)
    name = fields.CharField(max_length=1024, null=False)

    campaigns: fields.ReverseRelation['Campaigns']
    scores: fields.ReverseRelation['MLScores']

    telegram_users: fields.ReverseRelation['TelegramUsers']


class CampaignsTargeting(Model):
    id = fields.UUIDField(pk=True, null=False)
    gender: TargetingGender = fields.CharEnumField(enum_type=TargetingGender, null=True)
    age_from = fields.IntField(null=True)
    age_to = fields.IntField(null=True)
    location = fields.CharField(max_length=1024, null=True)

    campaign: fields.ReverseRelation['Campaigns']


class Campaigns(Model):
    id = fields.UUIDField(pk=True, null=False)
    advertiser: fields.ForeignKeyRelation[Advertisers] = fields.ForeignKeyField(
        model_name='models.Advertisers', related_name='campaigns', null=False
    )
    impressions_limit = fields.IntField(null=False)
    clicks_limit = fields.IntField(null=False)
    cost_per_impression = fields.FloatField(null=False)
    cost_per_click = fields.FloatField(null=False)
    ad_title = fields.CharField(max_length=1024, null=False)
    ad_text = fields.TextField(null=False)
    ad_image = fields.CharField(max_length=1024, null=True)
    start_date = fields.BigIntField(null=False)
    end_date = fields.BigIntField(null=False)
    targeting: fields.OneToOneRelation[CampaignsTargeting] = fields.OneToOneField(
        model_name='models.CampaignsTargeting', related_name='campaign', null=False
    )

    impressions: fields.ReverseRelation['CampaignImpressions']
    clicks: fields.ReverseRelation['CampaignClicks']


class MLScores(Model):
    id = fields.UUIDField(pk=True, null=False)
    client: fields.ForeignKeyRelation[Clients] = fields.ForeignKeyField(
        model_name='models.Clients', related_name='scores', null=False
    )
    advertiser: fields.ForeignKeyRelation[Advertisers] = fields.ForeignKeyField(
        model_name='models.Advertisers', related_name='scores', null=False
    )
    score = fields.IntField(null=False)


class CampaignImpressions(Model):
    id = fields.UUIDField(pk=True, null=False)
    client: fields.ForeignKeyRelation[Clients] = fields.ForeignKeyField(
        model_name='models.Clients', related_name='impressions', null=False
    )
    campaign: fields.ForeignKeyRelation[Campaigns] = fields.ForeignKeyField(
        model_name='models.Campaigns', related_name='impressions', null=False
    )
    price = fields.FloatField(null=False)
    date = fields.BigIntField(null=False)


class CampaignClicks(Model):
    id = fields.UUIDField(pk=True, null=False)
    client: fields.ForeignKeyRelation[Clients] = fields.ForeignKeyField(
        model_name='models.Clients', related_name='clicks', null=False
    )
    campaign: fields.ForeignKeyRelation[Campaigns] = fields.ForeignKeyField(
        model_name='models.Campaigns', related_name='clicks', null=False
    )
    price = fields.FloatField(null=False)
    date = fields.BigIntField(null=False)


class TelegramUsers(Model):
    id = fields.UUIDField(pk=True, null=False)
    telegram_id = fields.BigIntField(null=False)
    chat_id = fields.BigIntField(null=False)

    advertiser: fields.ForeignKeyRelation[Advertisers] = fields.ForeignKeyField(
        model_name='models.Advertisers', related_name='telegram_users', null=False
    )
