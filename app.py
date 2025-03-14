from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "rahasia_admin"

EXCEL_FILE = "zakat_data.xlsx"
ADMIN_PASSWORD = "dpcbtg"

# Fungsi untuk membaca data dari Excel
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            return pd.read_excel(EXCEL_FILE, engine="openpyxl")
        except Exception as e:
            print("Error loading Excel file:", e)
            return pd.DataFrame(columns=["Nama", "Zakat Fitrah", "Zakat Kifarat", "Zakat Harta"])
    return pd.DataFrame(columns=["Nama", "Zakat Fitrah", "Zakat Kifarat", "Zakat Harta"])

# Fungsi untuk menyimpan data ke Excel
def save_data(df):
    try:
        df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    except Exception as e:
        print("Error saving Excel file:", e)

# Route halaman utama
@app.route('/')
def index():
    df = load_data()
    
    # Hitung total pembayaran zakat
    total_fitrah = df["Zakat Fitrah"].sum()
    total_kifarat = df["Zakat Kifarat"].sum()
    total_harta = df["Zakat Harta"].sum()

    return render_template(
        'index.html', 
        data=df.to_dict(orient='records'), 
        is_admin=session.get("is_admin", False),
        total_fitrah=total_fitrah,
        total_kifarat=total_kifarat,
        total_harta=total_harta
    )

# Route untuk login admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for('index'))
        else:
            return "Password salah! <a href='/login'>Coba lagi</a>"

    return render_template('login.html')

# Route untuk logout admin
@app.route('/logout')
def logout():
    session.pop("is_admin", None)
    return redirect(url_for('index'))

# Route untuk menampilkan form tambah data
@app.route('/tambah_form', methods=['GET', 'POST'])
def tambah_form():
    if not session.get("is_admin"):
        return "Anda tidak memiliki akses untuk menambah data!", 403

    if request.method == 'POST':
        nama = request.form['nama']
        zakat_fitrah = int(request.form['zakat_fitrah'] or 0)
        zakat_kifarat = int(request.form['zakat_kifarat'] or 0)
        zakat_harta = int(request.form['zakat_harta'] or 0)

        df = load_data()
        new_entry = pd.DataFrame([{
            "Nama": nama, 
            "Zakat Fitrah": zakat_fitrah, 
            "Zakat Kifarat": zakat_kifarat, 
            "Zakat Harta": zakat_harta
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)

        return redirect(url_for('index'))

    return render_template('tambah.html')

# Route untuk download Excel (hanya untuk admin)
@app.route('/download-excel')
def download_excel():
    if session.get('is_admin'):
        return send_file(EXCEL_FILE, as_attachment=True)
    else:
        return "Akses ditolak. Anda bukan admin!"

# Route untuk halaman edit data
@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if not session.get("is_admin"):
        return "Anda tidak memiliki akses untuk mengedit data!", 403

    df = load_data()

    if request.method == 'POST':
        df.at[index, "Nama"] = request.form['nama']
        df.at[index, "Zakat Fitrah"] = int(request.form['zakat_fitrah'])
        df.at[index, "Zakat Kifarat"] = int(request.form['zakat_kifarat'])
        df.at[index, "Zakat Harta"] = int(request.form['zakat_harta'])
        save_data(df)
        return redirect(url_for('index'))

    return render_template('edit.html', index=index, data=df.iloc[index].to_dict())

if __name__ == '__main__':
    app.run(debug=True)
