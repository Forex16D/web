from application.services.db import DatabasePool
from application.services.portfolio_service import PortfolioService
from application.services.auth_service import AuthService
from application.services.user_service import UserService

from argon2 import PasswordHasher

class AppContainer:
  def __init__(self):
    self.db_pool = DatabasePool()
    self.hasher = PasswordHasher()
    self.portfolio_service = PortfolioService(self.db_pool)
    self.auth_service = AuthService(self.db_pool, self.hasher)
    self.user_service = UserService(self.db_pool)
    
container = AppContainer()