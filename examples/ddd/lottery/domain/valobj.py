from onto.attrs import attrs
from onto.models.base import Serializable as ValueObject


class AwardPool(ValueObject):
    award_pool_id: int = attrs.doc_id
    awards = attrs.set(attrs.embed('Award'))


class Award(ValueObject):
    award_id: int = attrs.doc_id
    probability: int = attrs.nothing


class DrawLotteryContext:

    mt_city_info = attrs.embed('MtCity')
    game_score: str = attrs.nothing
    lon: str = attrs.nothing
    lat: str = attrs.nothing
    user_id: int = attrs.nothing
    lottery_id: int = attrs.nothing

    @lottery_id.getter
    def lottery_id(self):
        return 123


class IssueResponse(ValueObject):

    code: int = attrs.nothing
    prize_info = attrs.embed('PrizeInfo')  # TODO: PrizeInfo

