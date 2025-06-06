from application.services.db import DatabasePool
from application.services.portfolio_service import PortfolioService
from application.services.auth_service import AuthService
from application.services.user_service import UserService
from application.services.mt_services import MtService
from application.services.model_service import ModelService
from application.services.market_data_service import MarketDataService
from application.services.billing_service import BillingService
from application.services.admin_service import AdminService

from argon2 import PasswordHasher # type: ignore

class AppContainer:
  def __init__(self):
    self.db_pool = DatabasePool()
    self.hasher = PasswordHasher()
    self.portfolio_service = PortfolioService(self.db_pool)
    self.auth_service = AuthService(self.db_pool, self.hasher)
    self.user_service = UserService(self.db_pool)
    self.mt_service = MtService(self.db_pool)
    self.model_service = ModelService(self.db_pool)
    self.market_data_service = MarketDataService(self.db_pool)
    self.billing_service = BillingService(self.db_pool)
    self.admin_service = AdminService(self.db_pool)

container = AppContainer()