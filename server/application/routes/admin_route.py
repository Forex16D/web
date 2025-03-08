from flask import request, Blueprint # type: ignore

from application.controllers.admin_controller import AdminController
from application.container import container

admin_routes = Blueprint("admin_routes", __name__)
admin_controller = AdminController(container.admin_service)

@admin_routes.route("/v1/admin/dashboard", methods=["GET"])
def get_dashboard():
  return admin_controller.get_dashboard()

