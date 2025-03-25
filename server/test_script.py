from application.container import container

bill_service = container.billing_service
bill_service.pay_all_expert()

# portfolio_service = container.portfolio_service
# portfolios = portfolio_service.get_expert_portfolios()
# print(portfolios)