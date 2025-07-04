#!/usr/bin/env python3
"""
Database initialization script for GPO
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD', 'UCOXZibz5OLgTofg')
SUPABASE_HOST = os.getenv('SUPABASE_HOST', 'db.dbbpghthgnwozewmlzes.supabase.co')
SUPABASE_PORT = os.getenv('SUPABASE_PORT', '6543')
SUPABASE_DB = os.getenv('SUPABASE_DB', 'postgres')
SUPABASE_USER = os.getenv('SUPABASE_USER', 'postgres.dbbpghthgnwozewmlzes')

def init_db():
    """Initialize the database with the schema"""
    print('Connecting to database...')
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            dbname=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cur = conn.cursor()
        
        print('Reading schema file...')
        # Read the schema file
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print('Executing schema...')
        # Execute the schema
        cur.execute(schema_sql)
        
        print('Schema executed successfully!')
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        print('Database initialized successfully!')
    except Exception as e:
        print(f'Error initializing database: {e}')
        sys.exit(1)

def create_demo_data():
    """Create demo data for testing"""
    print('Creating demo data...')
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            dbname=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Create a demo organization
        organization_id = '11111111-1111-1111-1111-111111111111'
        cur.execute(
            """
            INSERT INTO organizations (id, name, subscription_tier, subscription_status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (organization_id, 'Demo Organization', 'enterprise', 'active')
        )
        
        # Create a demo admin user
        from werkzeug.security import generate_password_hash
        admin_id = '22222222-2222-2222-2222-222222222222'
        admin_password_hash = generate_password_hash('admin123')
        cur.execute(
            """
            INSERT INTO users (id, email, name, password_hash, role, organization_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (admin_id, 'admin@demo.com', 'Admin User', admin_password_hash, 'admin', organization_id)
        )
        
        # Create demo linguists
        linguist_data = [
            ('John Smith', 'EN, FR', 'Legal', 85, 90, 'Low'),
            ('Maria Garcia', 'EN, ES', 'Medical', 92, 88, 'Medium'),
            ('David Lee', 'EN, ZH', 'Technical', 80, 95, 'High'),
            ('Sarah Johnson', 'EN, DE', 'Marketing', 88, 85, 'Low')
        ]
        
        for name, languages, specialty, speed, quality, load in linguist_data:
            # Create user for linguist
            import uuid
            user_id = str(uuid.uuid4())
            password_hash = generate_password_hash('linguist123')
            email = f"{name.lower().replace(' ', '.')}@demo.com"
            
            cur.execute(
                """
                INSERT INTO users (id, email, name, password_hash, role, organization_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
                """,
                (user_id, email, name, password_hash, 'linguist', organization_id)
            )
            
            result = cur.fetchone()
            if result:
                user_id = result[0]
                
                # Create linguist profile
                cur.execute(
                    """
                    INSERT INTO linguists (user_id, name, languages, specialties, speed_score, quality_score, current_load, organization_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, name, languages, specialty, speed, quality, load, organization_id)
                )
        
        # Create demo projects
        from datetime import datetime, timedelta
        
        # Get linguist IDs
        cur.execute("SELECT id FROM linguists WHERE organization_id = %s", (organization_id,))
        linguist_ids = [row[0] for row in cur.fetchall()]
        
        if linguist_ids:
            project_data = [
                ('Acme Corp', 'Website Localization', 'EN-FR', 'Marketing', 5000, 2500, linguist_ids[0], 'In Progress'),
                ('MediHealth', 'Medical Documentation', 'EN-ES', 'Medical', 8000, 0, linguist_ids[1], 'Not Started'),
                ('TechSolutions', 'User Manual', 'EN-ZH', 'Technical', 12000, 6000, linguist_ids[2], 'In Progress'),
                ('LegalFirm', 'Contract Translation', 'EN-DE', 'Legal', 3000, 3000, linguist_ids[3], 'Completed')
            ]
            
            for client, name, lang_pair, content, words, translated, linguist_id, status in project_data:
                start_date = datetime.now() - timedelta(days=10)
                due_date = datetime.now() + timedelta(days=10)
                
                cur.execute(
                    """
                    INSERT INTO projects (
                        client_name, project_name, language_pair, content_type,
                        start_date, due_date, initial_word_count, translated_words,
                        assigned_linguist_id, status, organization_id, created_by
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (client, name, lang_pair, content, start_date, due_date, words, translated,
                     linguist_id, status, organization_id, admin_id)
                )
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        print('Demo data created successfully!')
    except Exception as e:
        print(f'Error creating demo data: {e}')
        sys.exit(1)

if __name__ == '__main__':
    # Check if we should create demo data
    create_demo = len(sys.argv) > 1 and sys.argv[1] == '--demo'
    
    init_db()
    
    if create_demo:
        create_demo_data() 