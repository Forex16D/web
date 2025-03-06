from application.container import container

bill_service = container.billing_service

bill_service.bill_all()