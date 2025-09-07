import pandas as pd


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