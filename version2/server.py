from flask import Flask, jsonify
import pandas as pd
import random

app = Flask(__name__)

# Load the CSV file into a DataFrame
df = pd.read_csv('../data/test_data.csv')


@app.route('/random', methods=['GET'])
def get_random_line():
    if df.empty:
        return jsonify({'error': 'No data available'}), 500
    
    random_index = random.randint(0, len(df) - 1)
    random_row = df.iloc[random_index].to_dict()
    
    return jsonify(random_row)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
