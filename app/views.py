"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from flask import render_template, request, jsonify, send_from_directory, abort, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
from datetime import datetime
from . import app
from .db import db
from .model import User, Client, HairProfiles, DyeSession, FormulaArchive, StrandPredictions
from .forms import SignupForm, LoginForm, PhotoUploadForm, ClientForm, HairProfileForm
from .utils.s3 import upload_to_s3
from ai.damage_model import predict_damage
import numpy as np
import os


IMG_SIZE = 224
class_names = ["black", "brown", "blonde", "red"]  # match your training classes
model = load_model("path/to/your_model.h5")

###
# Routing for your application.
###

@app.route('/')
def home():
    return render_template("index.html")

# ============================================
# PREDICTION
# ============================================


@app.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image provided"}), 400

    # Step 1: Upload to S3, get URL back
    s3_url = upload_to_s3(file)

    # Step 2: Download from S3 into memory for the model
    import requests as http_requests
    from io import BytesIO

    img_data = http_requests.get(s3_url).content
    img = load_img(BytesIO(img_data), target_size=(IMG_SIZE, IMG_SIZE))

    # Step 3: Preprocess and predict
    img_array = preprocess_input(np.expand_dims(img_to_array(img), axis=0))
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions)]
    confidence = float(np.max(predictions) * 100)

    # Step 4: Return result with S3 URL
    return jsonify({
        "prediction": predicted_class,
        "confidence": f"{confidence:.2f}%",
        "image_url": s3_url
    })
    
@app.route('/analyze-damage', methods=['POST'])
@login_required
def analyze_damage():
    file = request.files.get('hair_image')

    if not file:
        return jsonify({"error": "No image provided"}), 400

    # 🔹 Run AI model
    result = predict_damage(file)

    return jsonify(result)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(
        user_name=data['username'],
        email=data['email']
    )

    new_user.set_password(data['password']) 
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.username,
            "email": user.email
        }
    })
    
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    client = Client(
        client_name=data['client_name'],
        userID=data.get('userID')
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({"id": client.clientID})

@app.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([
        {"id": c.clientID, "name": c.client_name, "userID": c.userID}
        for c in clients
    ])
    
@app.route('/clients/<int:id>', methods=['PUT'])
def update_client(id):
    client = Client.query.get_or_404(id)
    data = request.json
    client.client_name = data.get('client_name', client.client_name)
    db.session.commit()
    return jsonify({"message": "Updated"})

@app.route('/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Deleted"})

@app.route('/add-client', methods=['GET', 'POST'])
@login_required
def add_client():
    client_form = ClientForm()
    hair_form = HairProfileForm()

    if client_form.validate_on_submit() and hair_form.validate():
        # Create Client
        client = Client(
            client_name=client_form.client_name.data,
            userID=current_user.id
        )
        db.session.add(client)
        db.session.commit()

        # Create Hair Profile
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

        return redirect(url_for('dashboard'))

    return render_template('add_client.html', client_form=client_form, hair_form=hair_form)

@app.route('/edit-hair-profile/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit_hair_profile(profile_id):
    profile = HairProfiles.query.get_or_404(profile_id)
    form = HairProfileForm(obj=profile)

    if form.validate_on_submit():
        form.populate_obj(profile)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', form=form)

@app.route('/profiles', methods=['POST'])
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

@app.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = HairProfiles.query.all()
    return jsonify([
        {"id": p.profileID, "clientID": p.clientID}
        for p in profiles
    ])
    
@app.route('/profiles/<int:id>', methods=['DELETE'])
def delete_profile(id):
    profile = HairProfiles.query.get_or_404(id)
    db.session.delete(profile)
    db.session.commit()
    return jsonify({"message": "Deleted"})

@app.route('/sessions', methods=['POST'])
def create_session():
    file = request.files.get('hair_image')
    data = request.form

    if not file:
        return jsonify({"error": "Image required"}), 400

    # AI Prediction
    prediction = predict_damage(file)

    # Upload to S3
    image_url = upload_to_s3(file)

    # Save to DB
    session = DyeSession(
        profileID=data['profileID'],
        desired_shade=data.get('desired_shade'),
        developer_vol=data.get('developer_vol'),
        input_hair_pic_url=image_url
    )

    db.session.add(session)
    db.session.commit()

    # Save prediction
    pred = StrandPredictions(
        session_id=session.session_id,
        predicted_colour=data.get('desired_shade'),
        damage_risk=prediction['damage_risk'],
        damage_score=prediction['damage_score']
    )

    db.session.add(pred)
    db.session.commit()

    return jsonify({
        "session_id": session.session_id,
        "image_url": image_url,
        "prediction": prediction
    })

@app.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = DyeSession.query.all()
    return jsonify([
        {"id": s.session_id, "profileID": s.profileID}
        for s in sessions
    ])
    
@app.route('/sessions/<int:id>', methods=['DELETE'])
def delete_session(id):
    session = DyeSession.query.get_or_404(id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Deleted"})

@app.route('/formulas', methods=['POST'])
def create_formula():
    data = request.json
    formula = FormulaArchive(
        session_id=data.get('session_id'),
        formula_name=data.get('formula_name'),
        dye_brand=data.get('dye_brand'),
        developer_vol=data.get('developer_vol'),
        process_time=data.get('process_time')
    )
    db.session.add(formula)
    db.session.commit()
    return jsonify({"id": formula.formulaID})

@app.route('/formulas', methods=['GET'])
def get_formulas():
    formulas = FormulaArchive.query.all()
    return jsonify([
        {"id": f.formulaID, "name": f.formula_name}
        for f in formulas
    ])
    
@app.route('/formulas/<int:id>', methods=['DELETE'])
def delete_formula(id):
    formula = FormulaArchive.query.get_or_404(id)
    db.session.delete(formula)
    db.session.commit()
    return jsonify({"message": "Deleted"})

@app.route('/predictions', methods=['POST'])
def create_prediction():
    data = request.json
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

@app.route('/predictions', methods=['GET'])
def get_predictions():
    predictions = StrandPredictions.query.all()
    return jsonify([
        {"id": p.predictionID, "result": p.predicted_colour}
        for p in predictions
    ])
    
@app.route('/predictions/<int:id>', methods=['DELETE'])
def delete_prediction(id):
    prediction = StrandPredictions.query.get_or_404(id)
    db.session.delete(prediction)
    db.session.commit()
    return jsonify({"message": "Deleted"})


###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

