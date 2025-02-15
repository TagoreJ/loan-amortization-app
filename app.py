from flask import Flask, render_template, request, send_file
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

def calculate_amortization(principal, rate, years):
    rate = rate / 100 / 12  # Convert annual rate to monthly
    months = years * 12
    monthly_payment = (principal * rate) / (1 - (1 + rate) ** -months)
    
    balance = principal
    schedule = []
    
    for i in range(1, months + 1):
        interest = balance * rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        schedule.append([i, monthly_payment, principal_payment, interest, max(balance, 0)])
    
    return schedule

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        principal = float(request.form['principal'])
        rate = float(request.form['rate'])
        years = int(request.form['years'])
        amortization_table = calculate_amortization(principal, rate, years)
        return render_template('index.html', table=amortization_table)
    return render_template('index.html')

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    principal = float(request.form['principal'])
    rate = float(request.form['rate'])
    years = int(request.form['years'])
    amortization_table = calculate_amortization(principal, rate, years)
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(200, 750, "Loan Amortization Table")
    y = 700
    pdf.drawString(50, y, "Month")
    pdf.drawString(100, y, "Payment")
    pdf.drawString(200, y, "Principal")
    pdf.drawString(300, y, "Interest")
    pdf.drawString(400, y, "Balance")
    
    for row in amortization_table:
        y -= 20
        pdf.drawString(50, y, str(row[0]))
        pdf.drawString(100, y, f"{row[1]:.2f}")
        pdf.drawString(200, y, f"{row[2]:.2f}")
        pdf.drawString(300, y, f"{row[3]:.2f}")
        pdf.drawString(400, y, f"{row[4]:.2f}")
    
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="amortization.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
