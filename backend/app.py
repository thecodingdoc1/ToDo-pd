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
    cursor.execute('SELECT id, description, duedate, completed FROM tasks;')
    tasks = cursor.fetchall()
    conn.close()

    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task[0],
            'description':task[1],
            'duedate': task[2],
            'completed':task[3]
        })
    return jsonify(tasks_list)

@app.route('/api/tasks', methods=['POST'])
def add_tasks():
    data = request.json
    description = data.get('description')
    duedate = data.get('duedate')

    conn = None

    conn = get_db_connection()
    cursor = conn.cursor()
        
    # This is the line that might be failing:
    cursor.execute(
        'INSERT INTO tasks (description, duedate, completed) VALUES (%s, %s, %s) RETURNING id;', 
        (description, duedate, False) # Explicitly passing 'False' for completed
    )
        
    new_task_id = cursor.fetchone()[0]
    conn.commit()
        
    return jsonify({'id': new_task_id, 'description': description, 'duedate': duedate, 'completed': False}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'PUT':
            data = request.json
            completed = data.get('completed') 
            
            # --- CRITICAL UPDATE LOGIC ---
            cursor.execute(
                # Ensure 'completed' is the correct column name in your DB
                'UPDATE tasks SET completed = %s WHERE id = %s;', 
                (completed, task_id)
            )
            conn.commit()
            
            if cursor.rowcount == 0:
                # Task ID might be wrong or not found
                return jsonify({'message': 'Task not found'}), 404
            
            return jsonify({'message': 'Task updated'}), 200
        
        cursor.execute('DELETE FROM tasks WHERE id = %s;', (task_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': 'Task not found'}), 404
        return jsonify({'message': 'Task updated'}), 200

        # ... (rest of the DELETE logic)

    except Exception as e:
        print(f"Error in handle_task: {e}")
        if conn:
            conn.rollback()
        return jsonify({'error': 'Server error during update/delete'}), 500  
     
    finally:
        conn.close()

    return jsonify({'message': 'Task deleted'}), 200 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
