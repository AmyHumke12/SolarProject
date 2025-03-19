import os
import time

print("🔹 Running update_data.py...")

start_time = time.time()  # Track execution time

# Ensure Jupyter is installed
os.system("pip install nbconvert")

# Run the Jupyter Notebook
notebook_path = "BI_Solar_Production_Prediction.ipynb"
if os.path.exists(notebook_path):
    print(f"🚀 Running notebook: {notebook_path}")
    os.system(f"jupyter nbconvert --execute --to notebook --output executed_notebook.ipynb {notebook_path}")
    print("✅ Notebook execution completed.")
else:
    print(f"❌ Notebook not found: {notebook_path}")
    exit(1)

# Run the Streamlit app
app_path = "app.py"
if os.path.exists(app_path):
    print(f"🚀 Running Streamlit app: {app_path}")
    os.system(f"streamlit run {app_path} --server.headless true &")
    print("✅ Streamlit app executed.")
else:
    print(f"❌ Streamlit app not found: {app_path}")
    exit(1)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"🕒 Total Execution Time: {elapsed_time:.2f} seconds")
