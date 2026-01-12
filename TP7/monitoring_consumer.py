import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "machines-sensor-data",
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("Starting Monitoring Consumer...")
for message in consumer:
    data = message.value
    machine_id = data["machine_id"]
    temp = data["temperature"]
    vib = data["vibration"]
    status = data["status"]
    ts = data["timestamp"]

    print(f"[{ts}] Machine {machine_id} | Temp={temp}°C | Vib={vib} | Status={status}")

    if temp > 80 or vib > 10:
        print("  ⚠️  ALERTE PANNE POTENTIELLE !")
