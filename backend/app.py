import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    # Use environment variables for connection parameters
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=5432  # Explicitly state the port
    )
    return conn

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, description, completed FROM tasks;')
    tasks = cursor.fetchall()
    conn.close()

    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task[0],
            'description':task[1],
            'completed':task[2]
        })
    return jsonify(tasks_list)

@app.route('/api/tasks', methods=['POST'])
def add_tasks():
    data = request.json
    description = data.get('description')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (description) VALUES (%s) RETURNING id;', (description,))
    new_task_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'id': new_task_id, 'description': description, 'completed': False}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = %s;', (task_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Task deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
