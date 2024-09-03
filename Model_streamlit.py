import pandas as pd
import streamlit as st
from statsmodels.regression.linear_model import OLSResults
from statsmodels.tsa.ar_model import AutoReg
from sqlalchemy import create_engine
import seaborn as sns

# Load the OLS model
model = OLSResults.load("Reg_model.pickle")

# Function to predict footfalls
def predict(data, user, pw, db):

    engine = create_engine(f"mysql+pymysql://{user}:{pw}@localhost/{db}")
        
    prediction = pd.Series(model.predict(data))
    
    data["forecasted_Footfalls"] = pd.Series(prediction)
    
    data.to_sql('forecast_pred', con = engine, if_exists = 'replace', chunksize = 1000, index = False)

    
    # Only keep the 'Month' and 'forecasted_Footfalls' columns
    data = data[['Month', 'forecasted_Footfalls']]
    
    return data

def main():
    # Custom HTML and CSS
    st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
            color: #333;
        }
        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSRdbIRbRXQRV69dqZmo8ydSuU2ERnSLN_yg&s');
            background-size: cover;
            background-position: center;
        }
        .title {
            text-align: center;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            max-width: 600px;
        }
        .title h1 {
            color: red;
            font-family: 'Pacifico', cursive;
            margin: 0;
        }
        .title h2 {
            font-family: 'Arimo', sans-serif;
            font-size: 24px;
            color: #6abf69;
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
    <div class="container">
        <div class="title">
            <h1>Solutions by Data.The_Storyteller</h1>
            <h2>STRIDE_SIGHT: Forecasting Retail Footfalls</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader and user input
    st.sidebar.header("Upload File")
    uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return
    else:
        st.sidebar.warning("Please upload a CSV or Excel file.")
        return
    
    st.sidebar.header("Database Credentials")
    user = st.sidebar.text_input("UserID")
    pw = st.sidebar.text_input("Password", type="password")
    db = st.sidebar.text_input("Database")
    
    if st.sidebar.button("Predict"):
        if not user or not pw or not db:
            st.sidebar.warning("Please enter all database credentials.")
            return
        
        result = predict(data, user, pw, db)
        cm = sns.light_palette("blue", as_cmap=True)
        st.dataframe(result.style.background_gradient(cmap=cm).format(precision=2))

if __name__ == '__main__':
    main()
