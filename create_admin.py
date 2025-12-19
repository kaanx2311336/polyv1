from app import create_app, db
from app.models import User

app = create_app()

def create_admin():
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', email='admin@example.com', is_admin=True, is_seller=True)
            user.set_password('admin')
            db.session.add(user)
            db.session.commit()
            print("Admin user created (user: admin, pass: admin)")
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    create_admin()
