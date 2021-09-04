

class LotteryApplicationService:

    rest_connector = None

    lottery_service: None
    condition_service: None
    risk_service: None

    @rest_connector.triggers.on_post
    def participate_lottery(self, lottery_context):
        validate_login(lottery_context)
        risk_access_token = self.risk_service.acquire(
            lottery_context.risk_req
        )
        lottery_condition_res = self.condition_service.check_lottery_condition(
            lottery_context.lottery_id, lottery_context.user_id
        )
        issue_response = self.lottery_service.issue_lottery(lottery_context)

        if issue := issue_response:
            if issue.code == 200:
                return 'SuccessResponse'
            else:
                return 'ErrorResponse'


