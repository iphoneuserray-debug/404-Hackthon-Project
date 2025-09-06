import pandas as pd

# Read the Excel file, skipping the first two rows
df = pd.read_excel('sensor test 1.0 .xlsx', header = 2)
sensor_name = input("Enter the sensor name to search for: ")
result = df[df['Sensor'] == sensor_name]
print(result)

df = pd.DataFrame(result)
df.to_excel('output.xlsx', index=False)