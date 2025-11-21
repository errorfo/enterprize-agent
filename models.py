from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# --- Models ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(200))
    created_at = db.Column(db.String(50), default=datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {"id": self.id, "sku": self.sku, "name": self.name}

class InventoryBaseline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    
    @staticmethod
    def create_sample():
        sample = InventoryBaseline(sku='SKU123', quantity=2)
        db.session.add(sample)
        db.session.commit()
    
    def to_dict(self):
        return {"id": self.id, "sku": self.sku, "quantity": self.quantity}

class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300))
    filepath = db.Column(db.String(1000))
    uploaded_at = db.Column(db.String(50), default=datetime.utcnow().isoformat())
    status = db.Column(db.String(50), default='uploaded')
    meta = db.Column(db.PickleType, nullable=True)
    
    def to_dict(self):
        return {"id": self.id, "filename": self.filename, "status": self.status, "meta": self.meta}

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(80))
    image_id = db.Column(db.Integer)
    summary = db.Column(db.Text)
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.String(50), default=datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {"id": self.id, "sku": self.sku, "summary": self.summary, "status": self.status}

class MemoryBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(300), unique=True)
    value = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=datetime.utcnow().isoformat())
    
    def to_dict(self):
        return {"id": self.id, "key": self.key, "value": self.value}