"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .db import db
from ai.damage_model import predict_damage
from .models import User, Client, HairProfiles, DyeSession, FormulaArchive, StrandPredictions
from .forms import SignupForm, LoginForm, PhotoUploadForm, ClientForm, HairProfileForm
from .utils.s3 import upload_to_s3
from tensorflow.keras.models import load_model

import numpy as np
import os
from flask import flash


main = Blueprint('main', __name__)

# Tensorflow loaded safely — won't crash the app if missing
try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.utils import load_img, img_to_array
    from tensorflow.keras.applications.resnet50 import preprocess_input
    IMG_SIZE = 224
    class_names = ["breakage",
    "chemical_damage",
    "dry",
    "healthy",
    "heat_damage",
    "split_ends",]
    TENSORFLOW_AVAILABLE = True
except Exception:
    TENSORFLOW_AVAILABLE = False
    print("WARNING: TensorFlow not available. /predict route will be disabled.")

IMG_SIZE = 224
class_names = ["breakage",
    "chemical_damage",
    "dry",
    "healthy",
    "heat_damage",
    "split_ends",]


###
# Routing for your application.
###

@main.route('/test')
def test_page():
    return render_template('test.html')

@main.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@main.route('/login-page')
def login_page():
    return render_template('login.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/clients-page')
@login_required
def clients_page():
    return render_template('clients.html')

@main.route('/strand-test-page')
@login_required
def strand_test_page():
    return render_template('strand_test.html')

@main.route('/damage-page')
@login_required
def damage_page():
    return render_template('damage_assessment.html')

@main.route('/archive-page')
@login_required
def archive_page():
    return render_template('archive.html')

@main.route('/sessions-page')
@login_required
def sessions_page():
    return render_template('sessions.html')

@main.route('/profile-page')
@login_required
def profile_page():
    return render_template('profile.html')

@main.route('/')
def home():
    return render_template("index.html")

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login_page'))


# ============================================
# HEALTH CHECK  ← NEW: lets profile.html test the connection
# ============================================

@main.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


# ============================================
# PREDICTION (original — kept unchanged)
# ============================================

@main.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("image")

    if not file:
        return jsonify({"error": "No image provided"}), 400

    result = predict_damage(file)
    return jsonify(result)

# ============================================
# STRAND ANALYSIS — called by strand-test.html
# Two routes that do the same thing so both URL
# styles work (/analyze-damage and /api/predict/strand)
# ============================================

def _run_strand_analysis():
    """
    Shared logic for both strand analysis routes.
    Reads 'hair_image' from the multipart request,
    runs predict_damage(), uploads to S3, and returns
    the standard response shape the frontend expects:

        {
            "categories":  ["breakage", "dry"],
            "confidences": {"breakage": 0.91, "dry": 0.73, ...},
            "image_url":   "https://s3.amazonaws.com/...",
            "error":       null
        }
    """
    file = request.files.get('hair_image') or request.files.get('image')

    if not file:
        return jsonify({"error": "No image provided"}), 400

    from io import BytesIO
    file_bytes = BytesIO(file.read())   # read once into memory

    # Run AI model
    file_bytes.seek(0)
    result = predict_damage(file_bytes)

    # Upload to S3 (reset stream first)
    file_bytes.seek(0)
    file.stream = file_bytes
    image_url = upload_to_s3(file)

    # If TF unavailable, result already has 'error' key — still return it
    # with a 503 so the frontend can show a helpful message
    if result.get('error'):
        print("MODEL ERROR:", result)
    return jsonify({
        "categories": result.get("categories", []),
        "confidences": result.get("confidences", {}),
        "image_url": image_url,
        "error": result["error"]
    }), 503

    return jsonify({
        "categories":  result['categories'],
        "confidences": result['confidences'],
        "image_url":   image_url,
        "error":       None
    })


@main.route('/analyze-damage', methods=['POST'])
def analyze_damage():
    """Original route — kept so anything already calling it still works."""
    return _run_strand_analysis()


#@main.route('/api/predict/strand', methods=['POST'])
#@login_required
#def predict_strand():
    #"""New route — called by strand-test.html."""
    #return _run_strand_analysis()*\


# ============================================
# AUTH
# ============================================

@main.route('/signup', methods=['POST'])
def signup():
    data = request.json

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    # Log the user in immediately after signup
    login_user(new_user)

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id":    new_user.userID,
            "name":  new_user.username,
            "email": new_user.email
        }
    })


@main.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)

    return jsonify({
        "message": "Login successful",
        "user": {
            "id":    user.userID,
            "name":  user.username,
            "email": user.email
        }
    })




# ============================================
# CLIENTS
# ============================================

@main.route('/profiles/client/<int:client_id>', methods=['GET'])
def get_profile_by_client(client_id):
    profile = HairProfiles.query.filter_by(clientID=client_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify({
        "id": profile.profileID,
        "clientID": profile.clientID,
        "natural_colour": profile.natural_colour,
        "current_colour": profile.current_colour,
        "texture": profile.texture,
        "porosity": profile.porosity,
        "chem_history": profile.chem_history
    })

@main.route('/profiles/<int:id>', methods=['PUT'])
def update_profile(id):
    profile = HairProfiles.query.get_or_404(id)
    data = request.json
    profile.natural_colour = data.get('natural_colour', profile.natural_colour)
    profile.current_colour = data.get('current_colour', profile.current_colour)
    profile.texture = data.get('texture', profile.texture)
    profile.porosity = data.get('porosity', profile.porosity)
    profile.chem_history = data.get('chem_history', profile.chem_history)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"})

@main.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    client = Client(
        client_name=data['client_name'],
        userID=data.get('userID')
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({"id": client.clientID})


@main.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([
        {"id": c.clientID, "name": c.client_name, "userID": c.userID}
        for c in clients
    ])
    
@main.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    if not check_password_hash(current_user.password, data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 400
    current_user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({"message": "Password updated successfully"})
    
@main.route('/clients/<int:id>', methods=['PUT'])
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json
    client.client_name = data.get('client_name', client.client_name)
    db.session.commit()
    return jsonify({"message": "Updated"})


@main.route('/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Deleted"})


@main.route('/add-client', methods=['GET', 'POST'])
@login_required
def add_client():
    client_form = ClientForm()
    hair_form = HairProfileForm()

    if client_form.validate_on_submit() and hair_form.validate():
        client = Client(
            client_name=client_form.client_name.data,
            userID=current_user.id
        )
        db.session.add(client)
        db.session.commit()

        profile = HairProfiles(
            clientID=client.clientID,
            natural_colour=hair_form.natural_colour.data,
            current_colour=hair_form.current_colour.data,
            texture=hair_form.texture.data,
            porosity=hair_form.porosity.data,
            chem_history=hair_form.chem_history.data
        )
        db.session.add(profile)
        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template('add_client.html', client_form=client_form, hair_form=hair_form)


@main.route('/edit-hair-profile/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit_hair_profile(profile_id):
    profile = HairProfiles.query.get_or_404(profile_id)
    form = HairProfileForm(obj=profile)

    if form.validate_on_submit():
        form.populate_obj(profile)
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    return render_template('edit_profile.html', form=form)


# ============================================
# HAIR PROFILES
# ============================================

@main.route('/profiles', methods=['POST'])
def create_profile():
    data = request.json
    profile = HairProfiles(
        clientID=data['clientID'],
        natural_colour=data.get('natural_colour'),
        current_colour=data.get('current_colour'),
        texture=data.get('texture'),
        porosity=data.get('porosity'),
        chem_history=data.get('chem_history')
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({"id": profile.profileID})


@main.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = HairProfiles.query.all()
    return jsonify([
        {"id": p.profileID, "clientID": p.clientID}
        for p in profiles
    ])


@main.route('/profiles/<int:id>', methods=['DELETE'])
def delete_profile(id):
    profile = HairProfiles.query.get_or_404(id)
    db.session.delete(profile)
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ============================================
# DYE SESSIONS
# ============================================

@main.route('/sessions', methods=['POST'])
def create_session():
    file = request.files.get('hair_image')
    data = request.form

    if not file:
        return jsonify({"error": "Image required"}), 400

    prediction = predict_damage(file)
    image_url = upload_to_s3(file)

    session = DyeSession(
        profileID=data['profileID'],
        desired_shade=data.get('desired_shade'),
        developer_vol=data.get('developer_vol'),
        input_hair_pic_url=image_url
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "session_id": session.session_id,
        "image_url": image_url,
        "prediction": prediction
    })


@main.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = DyeSession.query.all()
    return jsonify([
        {"id": s.session_id, "profileID": s.profileID}
        for s in sessions
    ])


@main.route('/sessions/<int:id>', methods=['DELETE'])
def delete_session(id):
    session = DyeSession.query.get_or_404(id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ============================================
# FORMULA ARCHIVE
# ============================================

@main.route('/formulas', methods=['POST'])
def create_formula():
    data = request.json
    formula = FormulaArchive(
        session_id    = data.get('session_id'),
        formula_name  = data.get('formula_name'),
        dye_brand     = data.get('dye_brand'),
        developer_vol = data.get('developer_vol'),
        process_time  = data.get('process_time'),
        mode          = data.get('mode'),
        current_level = data.get('current_level'),
        target_level  = data.get('target_level'),
        shade         = data.get('shade'),
        texture       = data.get('texture'),
        porosity      = data.get('porosity'),
        damage_score  = data.get('damage_score'),
        notes         = data.get('notes'),
    )
    db.session.add(formula)
    db.session.commit()
    return jsonify({"id": formula.formulaID})


@main.route('/formulas', methods=['GET'])
def get_formulas():
    formulas = FormulaArchive.query.order_by(FormulaArchive.saved_at.desc()).all()
    return jsonify([
        {
            "id":            f.formulaID,
            "name":          f.formula_name,
            "dye_brand":     f.dye_brand,
            "developer_vol": f.developer_vol,
            "process_time":  f.process_time,
            "mode":          f.mode,
            "current_level": f.current_level,
            "target_level":  f.target_level,
            "shade":         f.shade,
            "texture":       f.texture,
            "porosity":      f.porosity,
            "damage_score":  f.damage_score,
            "notes":         f.notes,
            "saved_at":      f.saved_at.strftime('%Y-%m-%d') if f.saved_at else None,
        }
        for f in formulas
    ])


@main.route('/formulas/<int:id>', methods=['DELETE'])
def delete_formula(id):
    formula = FormulaArchive.query.get_or_404(id)
    db.session.delete(formula)
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ============================================
# STRAND PREDICTIONS (DB records)
# ============================================

@main.route('/predictions', methods=['POST'])
def create_prediction():
    data = request.json
    from .models import StrandPredictions
    prediction = StrandPredictions(
        session_id=data.get('session_id'),
        predicted_colour=data.get('predicted_colour'),
        damage_risk=data.get('damage_risk'),
        damage_score=data.get('damage_score'),
        process_time=data.get('process_time'),
        success_rate=data.get('success_rate'),
        test_date=data.get('test_date'),
        output_hair_pic_url=data.get('output_hair_pic_url')
    )
    db.session.add(prediction)
    db.session.commit()
    return jsonify({"id": prediction.predictionID})


@main.route('/predictions', methods=['GET'])
def get_predictions():
    from .models import StrandPredictions
    predictions = StrandPredictions.query.all()
    return jsonify([
        {"id": p.predictionID, "result": p.predicted_colour}
        for p in predictions
    ])


@main.route('/predictions/<int:id>', methods=['DELETE'])
def delete_prediction(id):
    from .models import StrandPredictions
    prediction = StrandPredictions.query.get_or_404(id)
    db.session.delete(prediction)
    db.session.commit()
    return jsonify({"message": "Deleted"})


###
# The functions below should be applicable to all Flask apps.
###

def form_errors(form):
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            )
            error_messages.append(message)
    return error_messages


@main.route('/<file_name>.txt')
def send_text_file(file_name):
    file_dot_text = file_name + '.txt'
    return current_app.send_static_file(file_dot_text)


@main.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@main.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404