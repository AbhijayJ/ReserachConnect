from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()  # Load environment variables from .env file

def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        cursor_factory=RealDictCursor
    )

def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        dbname="rc_db",
        user="postgres",
        password="Abhijay@97",
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor
    )

@app.route('/api/universities')
def get_universities():
    """Get all universities."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT uni_id, name FROM universities")
        universities = cur.fetchall()
        return jsonify(universities)
    finally:
        conn.close()

@app.route('/api/research-areas')
def get_research_areas():
    """Get all research areas."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT area FROM research_areas")
        areas = cur.fetchall()
        return jsonify(areas)
    finally:
        conn.close()

@app.route('/api/scholars')
def get_scholars():
    """Get scholars filtered by university and research area."""
    university = request.args.get('university')
    area = request.args.get('area')
    
    if not university or not area:
        return jsonify([])
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT p.id, p.name, p.title, p.photo
            FROM people p
            JOIN people_research_areas pra ON p.id = pra.id
            WHERE p.uni_id = %s AND pra.area = %s
        """, (university, area.lower()))
        scholars = cur.fetchall()
        return jsonify(scholars)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
