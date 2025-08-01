from app import create_app, db
from app.models import User, Role

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role}

@app.cli.command("init-roles")
def init_roles():
    """Create user roles"""
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)

    pharmacist_role = Role.query.filter_by(name='pharmacist').first()
    if not pharmacist_role:
        pharmacist_role = Role(name='pharmacist')
        db.session.add(pharmacist_role)

    db.session.commit()
    print('Roles have been created.')
