import streamlit as st

def model_b_page():
    st.title("Model B")
    st.write("This is the Model B page in the Models section.")
    
    st.subheader("Model B Specifications")
    st.write("Type: Regression Model")
    st.write("RMSE: 0.05")
    st.write("Training Data: 15,000 samples")
    
    st.subheader("Model B Usage")
    st.code("""
    # Example code for using Model B
    import model_b
    
    # Load the model
    model = model_b.load()
    
    # Make predictions
    predictions = model.predict(data)
    """, language="python")
    
    st.subheader("Performance Metrics")
    metrics = {
        "MSE": 0.0025,
        "MAE": 0.042,
        "R²": 0.96
    }
    st.json(metrics) 