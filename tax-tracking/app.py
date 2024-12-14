from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the TaxRecord model
class TaxRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.String(20), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tax_records = TaxRecord.query.all()
    due_date_filter = request.args.get('due_date', None)

    if due_date_filter:
        tax_records = [record for record in tax_records if record.due_date == due_date_filter]

    total_amount = sum(record.amount for record in tax_records)
    tax_rate = 0.06  # Example: 6% tax rate
    tax_due = total_amount * tax_rate

    return render_template('index.html', tax_records=tax_records, total_amount=total_amount, tax_due=tax_due, due_date_filter=due_date_filter)

@app.route('/add', methods=['POST'])
def add_record():
    company_name = request.form['company_name']
    amount = float(request.form['amount'])
    payment_date = request.form['payment_date']
    status = request.form['status']
    due_date = request.form['due_date']

    new_record = TaxRecord(company_name=company_name, amount=amount, payment_date=payment_date, status=status, due_date=due_date)
    db.session.add(new_record)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    record = TaxRecord.query.get_or_404(id)

    if request.method == 'POST':
        record.company_name = request.form['company_name']
        record.amount = float(request.form['amount'])
        record.payment_date = request.form['payment_date']
        record.status = request.form['status']
        record.due_date = request.form['due_date']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', record=record)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    record = TaxRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
