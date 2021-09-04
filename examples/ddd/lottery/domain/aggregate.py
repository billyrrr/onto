from onto.attrs import attrs


class DrawLottery:

    lottery_id: int = attrs.internal
    award_pools = attrs.set(attrs.embed('AwardPool')).internal

    def choose_award_pool(self, context: 'DrawLotteryContext') -> 'Award':
        if mt_city_info := context.mt_city_info:
            return self.choose_award_pool_by_city_info(award_pool_list=self.award_pools, mt_city_info=mt_city_info)
        else:
            return self.choose_award_pool_by_score(
                award_pool_list=self.award_pools,
                game_score=context.game_score
            )

    @staticmethod
    def choose_award_pool_by_score(award_pool_list: set, game_score: str):
        for award_pool in award_pool_list:
            if award_pool.match_score(game_score):
                return award_pool
        else:
            return None

    @staticmethod
    def choose_award_pool_by_city_info(award_pool_list: set, mt_city_info: 'MtCity'):
        for award_pool in award_pool_list:
            if award_pool.match_city(mt_city_info.city_id):
                return award_pool
        else:
            return None

