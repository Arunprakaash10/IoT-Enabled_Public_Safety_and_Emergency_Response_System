import serial
import psycopg2
import time

# Configure the serial connection
arduino_port = '/dev/tty.usbmodem14101'  # Update with your actual port
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

# PostgreSQL database connection parameters
db_host = 'your-google-cloud-ip'        # IP of your Google Cloud PostgreSQL instance
db_name = 'your-database-name'
db_user = 'your-database-user'
db_password = 'your-database-password'
db_port = 5432  # Default port for PostgreSQL

# Connect to the PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to insert data into PostgreSQL
def insert_data(temperature, humidity, light_level, smoke_level, motion_detected, panic_pressed):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO sensor_data (
                    temperature, humidity, light_level, smoke_level, motion_detected, panic_pressed
                )
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (temperature, humidity, light_level, smoke_level, motion_detected, panic_pressed))
            conn.commit()
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error inserting data: {e}")
        finally:
            cursor.close()
            conn.close()

# Main loop to read sensor data from Arduino and save to PostgreSQL
def main():
    while True:
        # Read data from the serial line
        data = ser.readline().decode('utf-8').strip()

        if data:
            # Parse the data (assuming comma-separated values)
            try:
                sensor_values = data.split(',')
                if len(sensor_values) == 6:
                    temperature = float(sensor_values[0])
                    humidity = float(sensor_values[1])
                    light_level = int(sensor_values[2])
                    smoke_level = int(sensor_values[3])
                    motion_detected = bool(int(sensor_values[4]))
                    panic_pressed = bool(int(sensor_values[5]))

                    # Insert data into PostgreSQL
                    insert_data(temperature, humidity, light_level, smoke_level, motion_detected, panic_pressed)
                else:
                    print("Invalid data format received from Arduino.")
            except ValueError as ve:
                print(f"Error parsing data: {ve}")

        time.sleep(1)  # Delay between reads

if __name__ == "__main__":
    main()
