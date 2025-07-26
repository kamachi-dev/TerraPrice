from flask import render_template, request
from model.Query import search_region

def register_routes(app):
    @app.route("/search")
    def show_student():
        region = request.args.get("region")
        student_data = search_region(region)
        return render_template("test.html", student=student_data)

    

