from flask import render_template, request, redirect, url_for, session, flash, jsonify
from model.Query import authenticate_user, get_categories, get_commodities_by_category, add_dataset_entry, create_user
from model.NN.estimator import *

def register_routes(app):
    @app.route("/")
    def index():
        return render_template("login.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            
            user = authenticate_user(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['isAdmin']
                return redirect(url_for('main'))
            else:
                flash('Invalid username or password', 'error')
        
        return render_template("login.html")
    
    @app.route("/register", methods=["POST"])
    def register():
        username = request.form.get("username")
        password = request.form.get("password")
        
        try:
            success, message = create_user(username, password)
            return jsonify({
                'success': success,
                'message': message
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'An error occurred during registration'
            })
    
    @app.route("/logout")
    def logout():
        session.clear()
        
        return redirect(url_for('login'))
    
    @app.route("/main")
    def main():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        categories = get_categories()
        return render_template("user/main.html", categories=categories)
    
    @app.route("/get_commodities/<category>")
    def get_commodities(category):
        commodities = get_commodities_by_category(category)
        return jsonify(commodities)
    
    @app.route("/predict_price", methods=["POST"])
    def predict_price():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        commodity = request.form.get("commodity")
        pricetype = request.form.get("pricetype")
        
        return jsonify({
            'success': True,
            'predicted_price': pred(longitude, latitude, commodity, pricetype),
            'location': f"Latitude: {latitude}, \n Longtitude: {longitude}",
            'commodity': commodity,
            'pricetype': pricetype
        })
    
    
    @app.route("/add_dataset", methods=["POST"])
    def add_dataset():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        data = {
            'latitude': request.form.get("latitude"),
            'longitude': request.form.get("longitude"),
            'category': request.form.get("category"),
            'commodity': request.form.get("commodity"),
            'pricetype': request.form.get("pricetype"),
            'value': request.form.get("value")
        }
        
        success = add_dataset_entry(data)
        
        return jsonify({
            'success': success,
            'message': 'Dataset entry added successfully' if success else 'Failed to add dataset entry'
        })

