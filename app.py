from flask import Flask, render_template, request, send_file
import pandas as pd
import pdfkit
from io import BytesIO

app = Flask(__name__)

def calculate_amortization(principal, rate, years):
    monthly_rate = rate / (12 * 100)
    months = years * 12
    emi = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    
    schedule = []
    balance = principal
    for i in range(1, months + 1):
        interest = balance * monthly_rate
        principal_payment = emi - interest
        balance -= principal_payment
        schedule.append([i, f"{emi:.2f}", f"{principal_payment:.2f}", f"{interest:.2f}", f"{balance:.2f}"])
    
    return schedule

@app.route('/', methods=['GET', 'POST'])
def index():
    table = None
    if request.method == 'POST':
        principal = float(request.form['principal'])
        rate = float(request.form['rate'])
        years = int(request.form['years'])
        table = calculate_amortization(principal, rate, years)
    return render_template('index.html', table=table)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    principal = float(request.form['principal'])
    rate = float(request.form['rate'])
    years = int(request.form['years'])
    table = calculate_amortization(principal, rate, years)
    
    df = pd.DataFrame(table, columns=["Month", "EMI", "Principal Paid", "Interest Paid", "Remaining Balance"])
    html_table = df.to_html(index=False, border=0)
    
    html = f'''
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f0f8ff; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #d1e7dd; }}
            tr:nth-child(odd) {{ background-color: #f8d7da; }}
        </style>
    </head>
    <body>
        <h2 style="color: blue; text-align: center;">📄 Loan Amortization Table</h2>
        {html_table}
        <h4 style="text-align: right; color: red;">🚀 Made by Tagore J</h4>
    </body>
    </html>
    '''
    
    pdf = pdfkit.from_string(html, False)
    response = BytesIO(pdf)
    return send_file(response, as_attachment=True, download_name="amortization_table.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
