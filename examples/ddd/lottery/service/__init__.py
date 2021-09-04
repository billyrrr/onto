from lottery.domain.valobj import DrawLotteryContext, IssueResponse


class LotteryService:
    award_count_facade = None
    user_city_info_facade = None
    award_send_service = None

    def issue_lottery(self, context: 'DrawLotteryContext'):
        from lottery.domain.aggregate import DrawLottery
        lottery: DrawLottery = DrawLottery.get(lottery_id=context.lottery_id)
        self.award_count_facade.increase_try_count(context)
        mt_city_info = self.user_city_info_facade.get_mt_city_info(context)
        context.mt_city_info = mt_city_info
        award_pool = lottery.choose_award_pool(context)
        award = award_pool.random_get_award()
        _ = self.award_send_service.send_award(award, context)
        return IssueResponse.new()
