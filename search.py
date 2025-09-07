import pandas as pd


def search_excel(sensor_name):
    df = pd.read_excel('sensor test 1.0 .xlsx', header= 2)
    if 'sensor' not in df.columns:
        raise ValueError("Column 'Sensor' not found")
    result = df[df['sensor'].astype(str) == str(sensor_name)]

    if 'i2c_functionality' in result.columns:
        result['i2c_functionality'] = result['i2c_functionality'].apply(
            lambda x: (
                f"✅ {x}" if str(x).strip().lower() == 'working'
                else f"🔘 {x}" if str(x).strip().lower() == 'offline'
                else f"🟠 {x}" if str(x).strip().lower() == 'affected'
                else f"❌ {x}"
            )
        )
    
    return result