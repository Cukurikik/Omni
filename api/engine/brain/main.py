import sys, json

def process(data):
    # Logika Bisnis Python Anda (OpenCV, TensorFlow, etc)
    return {"status": "success", "job_id": data.get('id', 'unknown')}

if __name__ == "__main__":
    input_data = json.loads(sys.stdin.read())
    print(json.dumps(process(input_data)))