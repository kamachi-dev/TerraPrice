import os
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from Model.Query import (
    authenticate_user, get_categories, get_commodities_by_category,
    add_dataset_entry, create_user, get_all_datasets, get_latest_datasets,
    get_datasets_paginated, get_total_datasets_count, get_profile
)
from Model.SupabaseClient import get_client
from Model.NN.estimator import *


def register_routes(app):
    @app.route("/")
    def index():
        return render_template("login.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            result = authenticate_user(email, password)
            if result and "_error" not in result:
                session["user_id"] = result["id"]
                session["username"] = result["username"]
                session["is_admin"] = result["isAdmin"]

                if result["isAdmin"]:
                    return redirect(url_for("admin"))
                else:
                    return redirect(url_for("main"))
            else:
                msg = result.get("_error", "Invalid email or password") if result else "Invalid email or password"
                flash(msg, "error")

        return render_template("login.html")

    @app.route("/register", methods=["POST"])
    def register():
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            success, message = create_user(email, password, username)
            return jsonify({
                "success": success,
                "message": message,
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "An error occurred during registration",
            })

    @app.route("/login/google")
    def login_google():
        client = get_client()
        site_url = os.environ.get("SITE_URL", request.url_root.rstrip("/"))
        redirect_to = site_url.rstrip("/") + "/auth/callback"
        res = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": redirect_to},
        })
        return redirect(res.url)

    @app.route("/auth/callback")
    def auth_callback():
        code = request.args.get("code")
        if code:
            client = get_client()
            try:
                res = client.auth.exchange_code_for_session(code)
                user = res.user
                profile = client.table("profiles").select("*").eq("id", user.id).execute()
                p = profile.data[0] if profile.data else {}
                session["user_id"] = user.id
                session["username"] = p.get("username", user.email.split("@")[0])
                session["is_admin"] = p.get("role") == "admin"
                return redirect(url_for("main"))
            except Exception as e:
                flash(str(e), "error")
        else:
            flash("Missing auth code", "error")
        return redirect(url_for("login"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/main")
    def main():
        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("is_admin"):
            return redirect(url_for("admin"))

        categories = get_categories()
        return render_template("user/main.html", categories=categories)

    @app.route("/get_categories")
    def get_cat():
        return jsonify(get_categories())

    @app.route("/admin")
    def admin():
        if "user_id" not in session:
            return redirect(url_for("login"))

        if not session.get("is_admin"):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("main"))

        return render_template("admin/admin.html")

    @app.route("/admin/datasets")
    def admin_datasets():
        if "user_id" not in session or not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 403

        page = request.args.get("page", 1, type=int)
        limit = 50
        offset = (page - 1) * limit

        datasets = get_datasets_paginated(limit, offset)
        total_count = get_total_datasets_count()
        total_pages = (total_count + limit - 1) // limit

        return jsonify({
            "datasets": datasets,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "limit": limit,
            },
        })

    @app.route("/admin/latest-datasets")
    def admin_latest_datasets():
        if "user_id" not in session or not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 403

        latest_datasets = get_latest_datasets(5)
        return jsonify(latest_datasets)

    @app.route("/admin/train", methods=["POST"])
    def train_model():
        if "user_id" not in session or not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 403

        try:
            train()
            return jsonify({
                "success": True,
                "message": "Model retrained successfully with latest dataset",
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Training failed: {str(e)}",
            })

    @app.route("/get_commodities/<category>")
    def get_commodities(category):
        commodities = get_commodities_by_category(category)
        return jsonify(commodities)

    @app.route("/predict_price", methods=["POST"])
    def predict_price():
        if "user_id" not in session:
            return redirect(url_for("login"))

        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        commodity = request.form.get("commodity")
        pricetype = request.form.get("pricetype")
        pred_price = pred(longitude, latitude, commodity, pricetype)
        return jsonify({
            "success": True,
            "predicted_price": pred_price,
            "location": f"Latitude: {latitude}, \n Longtitude: {longitude}",
            "commodity": commodity,
            "pricetype": pricetype,
        })

    @app.route("/add_dataset", methods=["POST"])
    def add_dataset():
        if "user_id" not in session:
            return redirect(url_for("login"))

        data = {
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
            "category": request.form.get("category"),
            "commodity": request.form.get("commodity"),
            "pricetype": request.form.get("pricetype"),
            "value": request.form.get("value"),
        }

        success = add_dataset_entry(data, user_id=session["user_id"])

        return jsonify({
            "success": success,
            "message": "Dataset entry added successfully" if success else "Failed to add dataset entry",
        })
