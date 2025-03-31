from application.container import container

bill_service = container.billing_service
container.bill_service.pay_all_expert()
bill_service.bill_all()


# portfolio_service = container.portfolio_service
# portfolios = portfolio_service.get_expert_portfolios()
# print(portfolios)