from flask import Flask, render_template, request, send_file, make_response
from werkzeug.utils import secure_filename
from csp import *

app = Flask(__name__)


application = app

@app.route("/")
def home():
    return render_template("home.html",  len= len(shift_records), shift_records=shift_records)
    
@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/home', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        shift_times = []
        for key, value in request.form.items():
            shift_times.append(int(value))
        volunteers = request.files['Volunteers']
        volunteers.save(secure_filename(volunteers.filename))

        shifts = request.files['Shifts']
        shifts.save(secure_filename(shifts.filename))

        response_csv = volunteers.filename

        shift_csv = shifts.filename

        assignments = get_data(response_csv, shift_csv, shift_times)

        resp = make_response(assignments.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=automated_schedule.csv"
        resp.headers["Content-Type"] = "text/csv"

        return resp

@app.route('/home')
def get_data(response_csv, shift_csv, lower_bounds):
    return read_csvs(response_csv, shift_csv, lower_bounds)

@app.route('/home')
def run_algorithm():
    responses, shifts, recovery_shifts, hours = get_data()
    final_schedule = csp.run_csp(responses, shifts, recovery_shifts, hours)
    print(final_schedule.head())
    return final_schedule
    
if __name__ == "__main__":
    app.run(debug=True)