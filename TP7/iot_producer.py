import json
import random
import time
from datetime import datetime

from kafka import KafkaProducer

# نجهز Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

MACHINE_IDS = ["M1", "M2", "M3"]

def generate_sensor_data():
    machine_id = random.choice(MACHINE_IDS)
    temperature = round(random.uniform(40, 100), 2)   # درجة حرارة
    vibration = round(random.uniform(0, 15), 2)       # اهتزاز
    status = "OK"

    if temperature > 80 or vibration > 10:
        status = "WARNING"

    return {
        "machine_id": machine_id,
        "temperature": temperature,
        "vibration": vibration,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("Starting IoT Producer...")
    while True:
        data = generate_sensor_data()
        producer.send("machines-sensor-data", value=data)
        print("Sent:", data)
        time.sleep(2)  # كل ثانيتين نبعث قراءة
