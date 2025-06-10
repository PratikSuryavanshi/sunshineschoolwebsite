from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# === TELEGRAM CONFIG ===
TELEGRAM_BOT_TOKEN = '7981471991:AAH2RfqEtkkJoF9GimFO1iwQdHl6rFJNeM8'
TELEGRAM_CHAT_ID = '597373694'

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram Error:", e)

# === DATABASE SETUP ===
def init_db():
    with sqlite3.connect('enquiries.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade TEXT,
            parent_name TEXT,
            phone TEXT UNIQUE,
            email TEXT,
            iam TEXT,
            comment TEXT
        )''')
# init_db()  # Uncomment if DB functionality is required

# === ROUTES ===
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/admission')
def admission():
    return render_template('admission.html')

@app.route('/faculty')
def notices():
    return render_template('faculty.html')

@app.route('/connect', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        print(f"[FORM] Name: {name}, Email: {email}, Message: {message}")
        return "Thank you for contacting us!"
    return render_template('connect.html')

# === Old Enquiry Form (Optional) ===
@app.route('/submit_enquiry', methods=['POST'])
def submit_enquiry():
    if request.is_json:
        data = request.get_json()
        grade = data.get('grade')
        parent_name = data.get('parent_name')
        phone = data.get('phone')
        email = data.get('email')
        iam = data.get('iam')
        comment = data.get('comment')
    else:
        grade = request.form.get('grade')
        parent_name = request.form.get('parentName')
        phone = request.form.get('phone')
        email = request.form.get('email')
        iam = request.form.get('iam')
        comment = request.form.get('comment')

    if not parent_name or not phone or len(phone) != 10 or not phone.isdigit():
        msg = "Invalid phone number or missing name"
        return jsonify({'success': False, 'error': msg}), 400 if request.is_json else msg

    message = (
        f"📥 New Enquiry\n"
        f"Grade: {grade}\nParent: {parent_name}\nPhone: {phone}\n"
        f"Email: {email or 'N/A'}\nI am: {iam}\nComment: {comment or 'N/A'}"
    )
    send_telegram_message(message)

    if request.is_json:
        return jsonify({'success': True})
    else:
        flash("Your enquiry has been submitted!", "success")
        return redirect(url_for('admission'))

# === NEW: Modal Admission Form Route ===
@app.route('/submit_admission', methods=['POST'])
def submit_admission():
    student_name = request.form.get('studentName')
    parent_name = request.form.get('parentName')
    contact = request.form.get('contact')
    grade = request.form.get('grade')
    notes = request.form.get('message')

    # Basic validation
    if not student_name or not parent_name or not contact or len(contact) != 10 or not contact.isdigit():
        flash("Invalid contact number or missing information", "danger")
        return redirect(url_for('home'))

    # Telegram message
    message = (
        f"📚 Admission Enquiry\n"
        f"Student: {student_name}\nParent: {parent_name}\nClass: {grade}\n"
        f"Phone: {contact}\nNotes: {notes or 'N/A'}"
    )
    send_telegram_message(message)

    # Optionally: Save to database here

    flash("Thank you! Your admission enquiry has been submitted.", "success")
    return redirect(url_for('home'))

# === START ===
if __name__ == '__main__':
    app.run(debug=True)
