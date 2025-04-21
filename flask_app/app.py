from flask import (
    Flask, render_template, request,
    session, send_file, redirect, url_for
)
import pickle, joblib, pandas as pd, io
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ----------------------------
# Load trained models (original absolute paths)
# ----------------------------
models = {
    'Logistic Regression': pickle.load(open(
        "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/logistic_regression_model.pkl", "rb"
    )),
    'SVM': pickle.load(open(
        "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/svm_model.pkl", "rb"
    )),
    'Decision Tree': pickle.load(open(
        "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/decision_tree_model.pkl", "rb"
    )),
    'Random Forest': pickle.load(open(
        "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/random_forest_model (2).pkl", "rb"
    )),
    'XGBoost': pickle.load(open(
        "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/xgboost_model.pkl", "rb"
    ))
}

# ----------------------------
# Load preprocessors (original absolute paths)
# ----------------------------
scaler           = joblib.load(
    "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/scaler.pkl"
)
poly             = joblib.load(
    "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/poly.pkl"
)
expected_columns = joblib.load(
    "D:/DA and DS Projects/Heart_Disease_Prediction/flask_app/models/expected_columns.pkl"
)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # 1) Collect & cast inputs
        features = [
            'age','sex','cp','trestbps','chol',
            'fbs','restecg','thalach','exang',
            'oldpeak','slope','ca','thal'
        ]
        raw = { f: float(request.form[f]) for f in features }

        # 2) Build DataFrame + engineered features
        df = pd.DataFrame([raw])
        df['thalach_oldpeak'] = df['thalach'] * df['oldpeak']
        df['cp_trestbps']     = df['cp'] * df['trestbps']
        df['age_bins']        = pd.cut(
            df['age'], bins=[0,40,55,70,100], labels=[0,1,2,3]
        )
        df['chol_bins']       = pd.cut(
            df['chol'], bins=[0,200,240,600], labels=[0,1,2]
        )
        df = pd.get_dummies(df, columns=['age_bins','chol_bins'])
        df = df.reindex(columns=expected_columns, fill_value=0)

        # 3) Polynomial & scaling
        X_poly   = poly.transform(df)
        X_scaled = scaler.transform(X_poly)

        # 4) Model predictions
        detailed = {}
        positives = 0
        for name, model in models.items():
            p = int(model.predict(X_scaled)[0])
            detailed[name] = (
                "High Chance of Heart Disease" if p == 1
                else "Low Chance of Heart Disease"
            )
            positives += p

        overall_pct  = round(positives / len(models) * 100)
        overall_text = f"{overall_pct}% chance that you have heart disease"

        # 5) Save for report, then re-render index.html with results
        session['report'] = {
            'inputs': raw,
            'overall_result': overall_text,
            'detailed': detailed
        }

        return render_template(
            'index.html',
            show_results=True,
            overall_result=overall_text,
            detailed=detailed,
            overall_pct=overall_pct
        )

    # GET → blank form
    return render_template('index.html', show_results=False)

@app.route('/generate_report')
def generate_report():
    data = session.get('report')
    if not data:
        return redirect(url_for('home'))

    # Friendly labels
    feature_map = {
        'age':'Age','sex':'Gender','cp':'Chest Pain Type',
        'trestbps':'Resting BP','chol':'Cholesterol','fbs':'Fasting BS',
        'restecg':'ECG','thalach':'Max HR','exang':'Exercise Angina',
        'oldpeak':'ST Depression','slope':'ST Slope','ca':'# Vessels',
        'thal':'Thalassemia'
    }

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial",'B',16)
    pdf.cell(0,10,"Heart Disease Prediction Report",ln=True,align="C")
    pdf.ln(8)

    # Inputs
    pdf.set_font("Arial",'B',14)
    pdf.cell(0,8,"User Inputs:",ln=True)
    pdf.set_font("Arial",'',12)
    for k,v in data['inputs'].items():
        pdf.cell(0,6,f"{feature_map.get(k,k)}: {v}",ln=True)
    pdf.ln(6)

    # Overall
    pdf.set_font("Arial",'B',14)
    pdf.cell(0,8,"Overall Prediction:",ln=True)
    pdf.set_font("Arial",'',12)
    pdf.cell(0,6,data['overall_result'],ln=True)
    pdf.ln(6)

    # Detailed
    pdf.set_font("Arial",'B',14)
    pdf.cell(0,8,"Model-by-Model Results:",ln=True)
    pdf.set_font("Arial",'',12)
    for m,pred in data['detailed'].items():
        pdf.cell(60,6,m,border=1)
        pdf.cell(0,6,pred,border=1,ln=True)

    pdf_bytes = io.BytesIO(pdf.output(dest='S').encode('latin1'))
    return send_file(
        pdf_bytes,
        as_attachment=True,
        download_name="heart_disease_report.pdf",
        mimetype="application/pdf"
    )


if __name__ == '__main__':
    app.run(debug=True)

  #                                   python flask_app\app.py