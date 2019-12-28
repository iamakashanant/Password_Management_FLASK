from flask_appbuilder import expose
from superset import appbuilder
from superset.views.base import BaseSupersetView


class SuperUserView(BaseSupersetView):
    route_base = '/superuser'

    @expose('/add', methods=['GET'])
    def addSuperuser(self):

        return self.render_template(
            'custom/users/add_superuser.html',
            is_custom=1
        )

    @expose('/signup', methods=['GET'])
    def signupDetails(self):
        return self.render_template(
            'custom/users/client_signup.html',
            is_custom=1
        )


appbuilder.add_view_no_menu(SuperUserView)
