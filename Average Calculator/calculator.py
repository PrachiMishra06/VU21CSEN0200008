from flask import Flask, jsonify, request
import requests
import time

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
numbers_window = []

# Third-party API endpoints
API_ENDPOINTS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'er': 'http://20.244.56.144/test/even',
    '1': 'http://20.244.56.144/test/rand'
}

def fetch_numbers(number_id):
    url = API_ENDPOINTS.get(number_id)
    if not url:
        return []
    
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            return data.get('numbers', [])
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException as e:
        pass
    
    return []

def update_window(new_numbers):
    global numbers_window
    
    # Keep only unique numbers and maintain window size
    for num in new_numbers:
        if num not in numbers_window:
            numbers_window.append(num)
    
    if len(numbers_window) > WINDOW_SIZE:
        numbers_window = numbers_window[-WINDOW_SIZE:]
    
    return numbers_window

@app.route('/numbers/<string:number_id>', methods=['GET'])
def get_numbers(number_id):
    prev_state = list(numbers_window)
    
    # Fetch numbers from the third-party server
    new_numbers = fetch_numbers(number_id)
    
    # Update the window with the new numbers
    current_state = update_window(new_numbers)
    
    if len(current_state) == WINDOW_SIZE:
        avg = sum(current_state) / WINDOW_SIZE
    else:
        avg = None
    
    response = {
        "windowPrevState": prev_state,
        "windowCurrState": current_state,
        "numbers": new_numbers,
        "avg": round(avg, 2) if avg is not None else None
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=9876)
