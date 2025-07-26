from flask import render_template, request
from Model.Query import search_region

def register_routes(app):
    @app.route("/search")
    def show_student():
        region = request.args.get("region")
        student_data = search_region(region)
        return render_template("student_info.html", student=student_data)
