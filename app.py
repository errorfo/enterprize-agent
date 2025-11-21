import os
import io
import zipfile
import uuid
from datetime import datetime
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, render_template_string
from werkzeug.utils import secure_filename
from models import db, init_db, Product, InventoryBaseline, ImageRecord, Ticket, MemoryBank

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///enterprise_agent.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

# Initialize DB
init_db(app)

# Simple homepage for demo
HOME_HTML = """
<h1>Enterprise Visual Inventory & QA — Demo</h1>
<p>Use the /upload endpoint (POST multipart/form-data) to upload images or a zip of images.</p>
<ul>
  <li>POST /upload — form-data: files[] (images) or zip_file (single zip)</li>
  <li>GET /images — list uploaded images (JSON)</li>
  <li>GET /tickets — list tickets (JSON)</li>
</ul>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/upload_form")
def upload_form():
    return """
    <h3>Upload Images</h3>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="files" multiple>
      <button type="submit">Upload</button>
    </form>
    """

@app.route("/upload", methods=["POST"])
def upload():
    """Accepts individual image files or a single ZIP file containing images.
    Stores files on disk, creates ImageRecord entries, and enqueues a stubbed ingestion task.
    """
    uploaded_files = []
    # Handle zip upload
    if "zip_file" in request.files:
        z = request.files["zip_file"]
        if z and z.filename.lower().endswith('.zip'):
            zf = zipfile.ZipFile(io.BytesIO(z.read()))
            for name in zf.namelist():
                if allowed_file(name):
                    data = zf.read(name)
                    filename = secure_filename(name)
                    unique = f"{uuid.uuid4().hex}_{filename}"
                    path = os.path.join(app.config["UPLOAD_FOLDER"], unique)
                    with open(path, "wb") as f:
                        f.write(data)
                    uploaded_files.append(path)
    else:
        # Handle multiple file uploads
        files = request.files.getlist('files')
        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                unique = f"{uuid.uuid4().hex}_{filename}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], unique)
                f.save(path)
                uploaded_files.append(path)
    # Store metadata in DB and create ingestion tasks (stub)
    results = []
    for file_path in uploaded_files:
        ir = ImageRecord(
            filename=os.path.basename(file_path),
            filepath=file_path,
            uploaded_at=datetime.utcnow().isoformat(),
            status="uploaded"
        )
        db.session.add(ir)
        db.session.commit()
        results.append({"id": ir.id, "filename": ir.filename})
        # STUB: enqueue ingestion -> vision pipeline
        # In a real implementation, this would push a message to a queue or start a background job
        # For starter demo we call the stub process synchronously
        _run_ingestion_pipeline(ir.id)
    return jsonify({"uploaded": results})

@app.route('/images', methods=['GET'])
def list_images():
    imgs = ImageRecord.query.order_by(ImageRecord.id.desc()).limit(100).all()
    data = [img.to_dict() for img in imgs]
    return jsonify(data)

@app.route('/tickets', methods=['GET'])
def list_tickets():
    tix = Ticket.query.order_by(Ticket.id.desc()).limit(100).all()
    return jsonify([t.to_dict() for t in tix])

# ---- Stubbed agent orchestration functions ---
def _run_ingestion_pipeline(image_record_id: int):
    """This is a simple synchronous orchestration that demonstrates the agent flow.
    Replace with background tasks, parallel agents, and model calls when moving to full implementation.
    """
    ir = ImageRecord.query.get(image_record_id)
    if not ir:
        app.logger.error(f"ImageRecord {image_record_id} not found")
        return
    # 1) Ingestion agent: preprocess (resize, normalize) — stubbed
    app.logger.info(f"Ingestion: preprocessing {ir.filepath}")
    ir.status = 'preprocessed'
    db.session.commit()
    # 2) Vision agent(s): run detection & defect models — STUB: fake detection results
    app.logger.info("Vision: running detection (stub)")
    detections = [
        {"sku": "SKU123", "bbox": [10, 10, 200, 200], "confidence": 0.92},
    ]
    defects = [
        {"type": "scratch", "bbox": [30, 40, 60, 80], "confidence": 0.78}
    ]
    ir.status = 'analyzed'
    ir.meta = {"detections": detections, "defects": defects}
    db.session.commit()
    # 3) Reconciliation agent: compare to inventory baseline (simple logic)
    app.logger.info("Reconciliation: comparing counts to baseline")
    # For demo: look up baseline quantity for detected SKU
    sku = detections[0]['sku']
    baseline = InventoryBaseline.query.filter_by(sku=sku).first()
    detected_count = len(detections)
    baseline_qty = baseline.quantity if baseline else 0
    if detected_count != baseline_qty:
        # Create ticket via Ticketing agent
        summary = f"Discrepancy for {sku}: baseline={baseline_qty}, detected={detected_count}"
        t = Ticket(
            sku=sku,
            image_id=ir.id,
            summary=summary,
            status='open',
            created_at=datetime.utcnow().isoformat()
        )
        db.session.add(t)
        db.session.commit()
        app.logger.info(f"Ticket created: {t.id}")
    # 4) Memory bank: store summary for long-term trends (stub)
    mb = MemoryBank(key=f"last_processed_{ir.id}", value=str({"sku": sku, "detected": detected_count}), created_at=datetime.utcnow().isoformat())
    db.session.add(mb)
    db.session.commit()
    return

if __name__ == '__main__':
    # Create example baseline if missing
    with app.app_context():
        if not InventoryBaseline.query.filter_by(sku='SKU123').first():
            InventoryBaseline.create_sample()
    app.run(debug=True)