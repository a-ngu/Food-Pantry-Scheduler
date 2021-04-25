from flask import Flask, render_template, request, send_file, make_response
from werkzeug.utils import secure_filename
from csp import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/home', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        volunteers = request.files['Volunteers']
        volunteers.save(secure_filename(volunteers.filename))
        recovery = request.files['Recovery']
        recovery.save(secure_filename(recovery.filename))
        shifts = request.files['Shifts']
        shifts.save(secure_filename(shifts.filename))

        print( "File saved successfully")

        response_csv = volunteers.filename
        recovery_csv = recovery.filename
        shift_csv = shifts.filename

        assignments = get_data(response_csv, shift_csv, recovery_csv)
        print(assignments.head())
        #assignments.to_csv(r"C:\Users\Aanika\Deskptop\new_assignments.csv")
        resp = make_response(assignments.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=automated_schedule.csv"
        resp.headers["Content-Type"] = "text/csv"

        return resp

@app.route('/home')
def get_data(response_csv, shift_csv, recovery_csv):
	return read_csvs(response_csv, shift_csv, recovery_csv)

@app.route('/home')
def run_algorithm():
	responses, shifts, recovery_shifts, hours = get_data()
	final_schedule = csp.run_csp(responses, shifts, recovery_shifts, hours)
	print(final_schedule.head())
	return final_schedule
    
if __name__ == "__main__":
    app.run(debug=True)