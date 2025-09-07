import pandas as pd
import tempfile

# Read the Excel file, skipping the first two rows
# def search_excel(query):
#     df = pd.read_excel('sensor test 1.0 .xlsx', header = 2)
#     result = df[df['Sensor'] == query]
#     with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
#         result.to_excel(tmp.result, index=False)
#         tmp.close()
#     return tmp.result

def search_excel(sensor_name):
    df = pd.read_excel('./logs/sensor_status.xlsx', engine="openpyxl")
    print (df)
    if 'sensor' not in df.columns:
        raise ValueError("Column 'Sensor' not found")
    result = df[df['sensor'].astype(str) == str(sensor_name)]

    if 'status' in result.columns:
        result['status'] = result['status'].apply(
            lambda x: (
                f"✅ {x}" if str(x).strip().lower() == 'working'
                else f"❌ {x}"
            )
        )
    
    return result