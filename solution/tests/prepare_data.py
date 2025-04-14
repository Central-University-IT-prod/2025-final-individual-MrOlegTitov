import asyncio
import string
from adsplatform.db import init_db
from adsplatform.db.models import (
    Advertisers,
    CampaignsTargeting,
    Campaigns,
    Clients,
    TargetingGender,
    MLScores,
    Gender,
)
from adsplatform.schemas.campaigns import Campaign, CampaignTargeting
from random import choice, randint

LOCATIONS = ['Moscow', 'SPb', 'Vladimir', 'T-Bank']


async def serialize_campaign(campaign: Campaigns) -> Campaign:
    advertiser: Advertisers = await campaign.advertiser
    targeting: CampaignsTargeting | None = await campaign.targeting

    return Campaign(
        campaign_id=campaign.id,
        advertiser_id=advertiser.id,
        impressions_limit=campaign.impressions_limit,
        clicks_limit=campaign.clicks_limit,
        cost_per_impression=campaign.cost_per_impression,
        cost_per_click=campaign.cost_per_click,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        targeting=CampaignTargeting(
            gender=targeting.gender,
            age_from=targeting.age_from,
            age_to=targeting.age_to,
            location=targeting.location,
        )
        if targeting
        else None,
    )


async def generate_client() -> Clients:
    return await Clients.create(
        login=''.join(
            [
                choice(string.ascii_letters + string.digits)
                for _ in range(randint(3, 15))
            ]
        ),
        age=randint(14, 55),
        location=choice(LOCATIONS),
        gender=choice(list(Gender)),
    )


async def generate_advertiser() -> Advertisers:
    return await Advertisers.create(
        name=''.join([choice(string.ascii_letters) for _ in range(randint(8, 20))])
    )


async def set_ml_score(advertiser: Advertisers, client: Clients) -> MLScores:
    score = (
        await MLScores.get_or_create(
            advertiser=advertiser, client=client, defaults={'score': 0}
        )
    )[0]
    score.score = randint(1, 100)
    await score.save()

    return score


async def generate_campaign(advertiser: Advertisers) -> Campaigns:
    age_from = randint(1, 50)
    age_to = randint(age_from, 50)
    target = await CampaignsTargeting.create(
        gender=choice(list(TargetingGender)),
        age_from=choice([age_from, None]),
        age_to=choice([age_to, None]),
        location=choice(LOCATIONS + [None]),
    )

    ad_name = f"{advertiser.id}: "
    if (
        not target.location
        and target.age_from is None
        and target.age_to is None
        and not target.gender
    ):
        ad_name += 'No target'
    else:
        ad_name += (
            f"{str(target.gender.value) or 'ALL'}, "
            f"{'From ' + str(target.age_from)}, "
            f"{'To ' + str(target.age_to)}', "
            f"{('In ' + target.location) if target.location else 'Everywhere'}"
        )

    campaign = await Campaigns.create(
        advertiser=advertiser,
        impressions_limit=randint(1, 10000),
        clicks_limit=randint(1, 10000),
        cost_per_impression=randint(1, 100) / 10,
        cost_per_click=randint(1, 200) / 10,
        ad_title=ad_name,
        ad_text='TODO',
        start_date=randint(0, 1),
        end_date=randint(2, 5),
        targeting=target,
    )
    desc = str((await serialize_campaign(campaign)).model_dump(exclude={'targeting'}))
    campaign.ad_text = desc
    await campaign.save()

    return campaign


async def main():
    await init_db(
        username='adsplatform',
        password='tXn!bazWDD#G83rk!X]7NF]X}g*8%h4',
        db_name='adsplatform',
    )
    clients_count = int(input('Clients amount: '))
    advertisers_count = int(input('Advertisers amount: '))
    campaigns_count = int(input('Campaigns amount: '))

    clients = [await generate_client() for _ in range(clients_count)]
    advertisers = [await generate_advertiser() for _ in range(advertisers_count)]
    for advertiser in advertisers:
        for _ in range(clients_count // 2):
            await set_ml_score(advertiser, choice(clients))

    [await generate_campaign(choice(advertisers)) for _ in range(campaigns_count)]

    print('Done!')
    print('Results:')
    print(f"Client IDs: {', '.join(map(lambda x: str(x.id), clients))}\n")
    print(f"Advertiser IDs: {', '.join(map(lambda x: str(x.id), advertisers))}\n")


if __name__ == '__main__':
    asyncio.run(main())
