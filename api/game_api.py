#!/usr/bin/env python3
"""
Paisabuddy Game Progress API Server
Serves game progress data to web frontend via REST API
"""

from flask import Flask, jsonify, request, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime, timedelta
import hashlib
import os
import sys

# Add games directory to path for database import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'games'))

try:
    from database import PaisabuddyDB, init_db, close_db
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️ Database module not found")
    DATABASE_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'paisabuddy_secret_key_2025'  # Change this to a secure key
CORS(app)  # Enable CORS for frontend access

# Global database instance
db = PaisabuddyDB() if DATABASE_AVAILABLE else None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if DATABASE_AVAILABLE and db and db.connect() else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/<username>/stats', methods=['GET'])
def get_user_stats(username):
    """Get comprehensive user statistics"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get user by username
        user = db.get_or_create_user(username)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get comprehensive stats
        stats = db.get_user_stats(user['id'])
        if not stats:
            return jsonify({'error': 'Failed to fetch stats'}), 500
        
        # Format the response
        response = {
            'user': {
                'id': stats['user']['id'],
                'name': stats['user']['name'],
                'username': stats['user']['username'],
                'total_score': stats['user']['total_score'],
                'balance': float(stats['user']['balance']) if stats['user']['balance'] else 0,
                'last_login': stats['user']['last_login'].isoformat() if stats['user']['last_login'] else None
            },
            'games': {
                'summary': stats.get('game_summary', []),
                'total_sessions': sum(game['sessions_played'] for game in stats.get('game_summary', [])),
                'highest_score': max((game['highest_score'] for game in stats.get('game_summary', []) if game['highest_score']), default=0)
            },
            'achievements': {
                'recent': stats.get('recent_achievements', []),
                'total': len(stats.get('recent_achievements', []))
            },
            'activity': {
                'streak_days': stats.get('streak_days', 0),
                'web_activities': stats.get('web_activity', []),
                'total_activities': sum(activity['activities_completed'] for activity in stats.get('web_activity', []))
            }
        }
        
        return jsonify(response)
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/user/<username>/recent-games', methods=['GET'])
def get_recent_games(username):
    """Get recent game sessions for user"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        user = db.get_or_create_user(username)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Get recent game sessions
        cursor.execute("""
            SELECT game_name, final_score, level_reached, session_start, session_end,
                   TIMESTAMPDIFF(MINUTE, session_start, session_end) as duration_minutes
            FROM GameSessions 
            WHERE user_id = %s 
            ORDER BY session_start DESC 
            LIMIT 20
        """, (user['id'],))
        
        sessions = cursor.fetchall()
        
        # Convert datetime objects to ISO format
        for session in sessions:
            if session['session_start']:
                session['session_start'] = session['session_start'].isoformat()
            if session['session_end']:
                session['session_end'] = session['session_end'].isoformat()
        
        cursor.close()
        return jsonify({'sessions': sessions})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/user/<username>/achievements', methods=['GET'])
def get_user_achievements(username):
    """Get all user achievements"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        user = db.get_or_create_user(username)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Get all achievements
        cursor.execute("""
            SELECT game_name, achievement_name, achievement_description, earned_at
            FROM GameAchievements 
            WHERE user_id = %s 
            ORDER BY earned_at DESC
        """, (user['id'],))
        
        achievements = cursor.fetchall()
        
        # Convert datetime objects to ISO format
        for achievement in achievements:
            if achievement['earned_at']:
                achievement['earned_at'] = achievement['earned_at'].isoformat()
        
        cursor.close()
        return jsonify({'achievements': achievements})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top users leaderboard"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        limit = request.args.get('limit', 10, type=int)
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        leaderboard = db.get_leaderboard(limit)
        
        return jsonify({'leaderboard': leaderboard})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/record-quiz', methods=['POST'])
def record_quiz_activity():
    """Record quiz activity from web frontend"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['username', 'quiz_name', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get or create user
        user = db.get_or_create_user(data['username'])
        if not user:
            return jsonify({'error': 'Could not create user'}), 500
        
        # Record the activity
        db.record_web_activity(
            user['id'],
            'quiz',
            data['quiz_name'],
            data['score'],
            data.get('time_spent', 0),
            data.get('answers')
        )
        
        return jsonify({
            'success': True,
            'message': 'Quiz activity recorded successfully',
            'user_total_score': user['total_score'] + data['score']
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/record-activity', methods=['POST'])
def record_general_activity():
    """Record general web activity"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['username', 'activity_type', 'activity_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        user = db.get_or_create_user(data['username'])
        if not user:
            return jsonify({'error': 'Could not create user'}), 500
        
        db.record_web_activity(
            user['id'],
            data['activity_type'],
            data['activity_name'],
            data.get('score', 0),
            data.get('time_spent', 0),
            data.get('activity_data')
        )
        
        return jsonify({
            'success': True,
            'message': 'Activity recorded successfully'
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/games/stats', methods=['GET'])
def get_games_stats():
    """Get overall game statistics"""
    if not DATABASE_AVAILABLE or not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Get game popularity stats
        cursor.execute("""
            SELECT game_name, 
                   COUNT(*) as total_sessions,
                   COUNT(DISTINCT user_id) as unique_players,
                   AVG(final_score) as avg_score,
                   MAX(final_score) as highest_score
            FROM GameSessions 
            GROUP BY game_name
            ORDER BY total_sessions DESC
        """)
        
        game_stats = cursor.fetchall()
        
        # Get total statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(DISTINCT user_id) as total_players,
                SUM(final_score) as total_points_earned
            FROM GameSessions
        """)
        
        total_stats = cursor.fetchone()
        
        cursor.close()
        
        return jsonify({
            'games': game_stats,
            'totals': total_stats
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Paisabuddy Game Progress API Server...")
    print("📊 Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/user/<username>/stats - User statistics")
    print("  GET  /api/user/<username>/recent-games - Recent game sessions")
    print("  GET  /api/user/<username>/achievements - User achievements")
    print("  GET  /api/leaderboard - Top users leaderboard")
    print("  POST /api/record-quiz - Record quiz activity")
    print("  POST /api/record-activity - Record general activity")
    print("  GET  /api/games/stats - Overall game statistics")
    print("\n🌐 Server running on http://localhost:5000")
    print("💡 Use CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)