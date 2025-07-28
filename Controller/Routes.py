from flask import render_template, request, redirect, url_for, session, flash, jsonify
from model.Query import authenticate_user, get_categories, get_commodities_by_category, add_dataset_entry, create_user, get_all_datasets, get_latest_datasets, get_datasets_paginated, get_total_datasets_count
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
                
                if user['isAdmin']:
                    return redirect(url_for('admin'))
                else:
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
        

        if session.get('is_admin'):
            return redirect(url_for('admin'))
        
        categories = get_categories()
        print(categories)
        return render_template("user/main.html", categories=categories)
    
    @app.route("/get_categories")
    def get_cat():
        return jsonify(get_categories())
    
    @app.route("/admin")
    def admin():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        

        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main'))
        
        return render_template("admin/admin.html")
    
    @app.route("/admin/datasets")
    def admin_datasets():
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        limit = 50
        offset = (page - 1) * limit
        
        datasets = get_datasets_paginated(limit, offset)
        total_count = get_total_datasets_count()
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        return jsonify({
            'datasets': datasets,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'limit': limit
            }
        })
    
    @app.route("/admin/latest-datasets")
    def admin_latest_datasets():
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        latest_datasets = get_latest_datasets(5)
        return jsonify(latest_datasets)
    
    @app.route("/admin/train", methods=["POST"])
    def train_model():
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            train()
            return jsonify({
                'success': True,
                'message': 'Model retrained successfully with latest dataset'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Training failed: {str(e)}'
            })
    
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
