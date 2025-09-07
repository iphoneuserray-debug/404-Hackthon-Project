import serial
import time

# Change 'COM3' to your Arduino's port (e.g., 'COM4', '/dev/ttyACM0' for Linux)
SERIAL_PORT = 'COM4'
BAUD_RATE = 115200

def read_sensor():
    try:
        start_time = time.time()
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(2)  # Wait for Arduino to reset
            print("Connected to Arduino. Reading data...")
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Received: {data}")
                if time.time() - start_time > 120:
                    print("2 minutes elapsed. Stopping read.")
                    break
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    read_sensor()