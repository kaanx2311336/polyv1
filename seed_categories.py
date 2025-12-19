from app import create_app, db
from app.models import Category

app = create_app()

def seed_categories():
    with app.app_context():
        # Check if already seeded
        if Category.query.count() > 0:
            print("Categories already exist.")
            return

        categories = [
            'Polymers', 'Chemicals', 'Technical', 'Scrap', 
            'Packaging', 'Machines', 'Services', 'Logistics'
        ]
        
        for name in categories:
            cat = Category(name=name)
            db.session.add(cat)
        
        db.session.commit()
        print("Categories seeded.")

if __name__ == '__main__':
    seed_categories()
