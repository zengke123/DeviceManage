from app import create_app, db, admin
from app.models import Host, Capacity
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_admin.contrib.sqla import ModelView

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Host=Host, Capacity=Capacity)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

admin.add_view(ModelView(Host, db.session, name="主机管理"))
admin.add_view(ModelView(Capacity, db.session, name="容量管理"))

if __name__ == '__main__':
    app.run()
