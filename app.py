from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import random
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# SMTP Configuration
# IMPORTANT: Update these with your Gmail credentials
# Or set as environment variables:
# Windows: set SMTP_EMAIL=your-email@gmail.com
# Windows: set SMTP_PASSWORD=your-app-password
# Linux/Mac: export SMTP_EMAIL=your-email@gmail.com
# Linux/Mac: export SMTP_PASSWORD=your-app-password



# In-memory storage (use database in production)
users_db = {}
otp_storage = {}

def send_otp_email(to_email, otp, purpose):
    """Send OTP email using Gmail SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'EcoLearn - Your Verification Code'
        msg['From'] = f"EcoLearn <{SMTP_EMAIL}>"
        msg['To'] = to_email
        
        # Email content
        if purpose == 'signup':
            purpose_text = "Verify your EcoLearn account"
        else:
            purpose_text = "Reset your EcoLearn password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 500px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
                .logo {{ text-align: center; font-size: 48px; margin-bottom: 10px; }}
                .title {{ text-align: center; color: #00cc6a; font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                .subtitle {{ text-align: center; color: #666; font-size: 16px; margin-bottom: 30px; }}
                .otp-box {{ background: linear-gradient(135deg, #00ff88, #00d4ff); border-radius: 15px; padding: 30px; text-align: center; margin: 20px 0; }}
                .otp-code {{ font-size: 42px; font-weight: bold; color: white; letter-spacing: 10px; text-shadow: 0 2px 10px rgba(0,0,0,0.2); }}
                .otp-label {{ color: rgba(255,255,255,0.9); font-size: 14px; margin-top: 10px; }}
                .info {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; font-size: 14px; color: #666; line-height: 1.6; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 0 10px 10px 0; font-size: 13px; color: #856404; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🌱</div>
                <div class="title">EcoLearn Verification</div>
                <div class="subtitle">{purpose_text}</div>
                
                <div class="otp-box">
                    <div class="otp-label">Your 6-digit verification code</div>
                    <div class="otp-code">{otp}</div>
                </div>
                
                <div class="warning">
                    <strong>⏰ Code expires in 10 minutes</strong><br>
                    For security, this code will expire after 10 minutes. If it expires, you can request a new one.
                </div>
                
                <div class="info">
                    <strong>Didn't request this?</strong><br>
                    If you didn't request this code, please ignore this email. Someone may have entered your email address by mistake.
                </div>
                
                <div class="footer">
                    🌍 Learn. Play. Save Earth.<br>
                    EcoLearn - Gamified Environmental Education Platform
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
EcoLearn Verification Code

Your 6-digit verification code: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

---
EcoLearn - Learn. Play. Save Earth.
"""
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        
        print(f"✅ OTP sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to user's email"""
    data = request.json
    email = data.get('email')
    purpose = data.get('purpose', 'signup')
    
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with expiration (10 minutes)
    otp_storage[email] = {
        'otp': otp,
        'purpose': purpose,
        'attempts': 0
    }
    
    # Send email
    success = send_otp_email(email, otp, purpose)
    
    if success:
        return jsonify({
            "success": True, 
            "message": "OTP sent successfully",
            "email": email
        })
    else:
        return jsonify({
            "success": False, 
            "message": "Failed to send email. Please try again."
        }), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP entered by user"""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({"success": False, "message": "Email and OTP are required"}), 400
    
    stored = otp_storage.get(email)
    
    if not stored:
        return jsonify({"success": False, "message": "OTP expired. Please request a new one."}), 400
    
    if stored['otp'] != otp:
        stored['attempts'] += 1
        if stored['attempts'] >= 3:
            del otp_storage[email]
            return jsonify({"success": False, "message": "Too many failed attempts. Please request a new OTP."}), 400
        return jsonify({"success": False, "message": f"Invalid OTP. {3 - stored['attempts']} attempts remaining."}), 400
    
    # OTP verified - remove from storage
    del otp_storage[email]
    
    return jsonify({
        "success": True, 
        "message": "OTP verified successfully",
        "purpose": stored['purpose']
    })

@app.route('/api/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP to user's email"""
    data = request.json
    email = data.get('email')
    purpose = data.get('purpose', 'signup')
    
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400
    
    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    
    # Update storage
    otp_storage[email] = {
        'otp': otp,
        'purpose': purpose,
        'attempts': 0
    }
    
    # Send email
    success = send_otp_email(email, otp, purpose)
    
    if success:
        return jsonify({"success": True, "message": "New OTP sent successfully"})
    else:
        return jsonify({"success": False, "message": "Failed to send email"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user after OTP verification"""
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    if not all([email, name, password]):
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    if email in users_db:
        return jsonify({"success": False, "message": "Email already registered"}), 400
    
    users_db[email] = {
        'name': name,
        'password': password,
        'email': email,
        'level': 1,
        'xp': 0,
        'coins': 100,
        'achievements': ['starter']
    }
    
    return jsonify({
        "success": True, 
        "message": "Account created successfully",
        "user": {
            'name': name,
            'email': email,
            'level': 1
        }
    })

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    
    user = users_db.get(email)
    
    if not user:
        return jsonify({"success": False, "message": "Account not found"}), 404
    
    if user['password'] != password:
        return jsonify({"success": False, "message": "Incorrect password"}), 401
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            'name': user['name'],
            'email': email,
            'level': user['level'],
            'xp': user['xp'],
            'coins': user['coins']
        }
    })

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset password after OTP verification"""
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not email or not new_password:
        return jsonify({"success": False, "message": "Email and new password are required"}), 400
    
    user = users_db.get(email)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    user['password'] = new_password
    
    return jsonify({"success": True, "message": "Password reset successfully"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "EcoLearn Email API"})

# ==================== ML ENDPOINTS ====================

# Import ML Engine
try:
    from ml_engine import ml_engine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML Engine not available. Install scikit-learn: pip install scikit-learn")

@app.route('/api/ml/status', methods=['GET'])
def ml_status():
    """Check ML system status"""
    if not ML_AVAILABLE:
        return jsonify({
            "ml_available": False,
            "message": "ML engine not installed. Run: pip install scikit-learn pandas numpy"
        })
    
    return jsonify({
        "ml_available": True,
        "algorithms": [
            "K-Means Clustering (User Segmentation)",
            "Decision Tree (Content Recommendation)",
            "Linear Regression (Performance Prediction)",
            "Gaussian Naive Bayes (Engagement Classification)",
            "Collaborative Filtering (Game Recommendations)"
        ],
        "models_trained": ml_engine.is_trained
    })

@app.route('/api/ml/user-clustering', methods=['POST'])
def ml_user_clustering():
    """K-Means Clustering: Segment users by learning behavior"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    if len(users_db) < 4:
        return jsonify({
            "algorithm": "K-Means Clustering",
            "error": "Need at least 4 users for clustering",
            "current_users": len(users_db)
        }), 400
    
    result = ml_engine.cluster_users(users_db)
    return jsonify(result)

@app.route('/api/ml/recommend-topic', methods=['POST'])
def ml_recommend_topic():
    """Decision Tree: Recommend learning topic for user"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    data = request.json
    email = data.get('email')
    
    if email not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    result = ml_engine.recommend_topic(users_db[email])
    return jsonify(result)

@app.route('/api/ml/predict-performance', methods=['POST'])
def ml_predict_performance():
    """Linear Regression: Predict user's next performance"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    data = request.json
    email = data.get('email')
    hours = data.get('hours_next_week', 5)
    
    if email not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    result = ml_engine.predict_performance(users_db[email], hours)
    return jsonify(result)

@app.route('/api/ml/predict-engagement', methods=['POST'])
def ml_predict_engagement():
    """Naive Bayes: Predict user engagement level"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    data = request.json
    email = data.get('email')
    
    if email not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    result = ml_engine.predict_engagement(users_db[email])
    return jsonify(result)

@app.route('/api/ml/collaborative-recommendations', methods=['POST'])
def ml_collaborative_recommendations():
    """Collaborative Filtering: Recommend games based on similar users"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    data = request.json
    email = data.get('email')
    n_recs = data.get('n_recommendations', 2)
    
    if email not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    result = ml_engine.collaborative_recommendations(email, users_db, n_recs)
    return jsonify(result)

@app.route('/api/ml/full-analytics', methods=['POST'])
def ml_full_analytics():
    """Comprehensive ML analytics for a user"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    data = request.json
    email = data.get('email')
    
    if email not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    result = ml_engine.generate_full_analytics(email, users_db)
    return jsonify(result)

@app.route('/api/ml/train-models', methods=['POST'])
def ml_train_models():
    """Train all ML models with current data"""
    if not ML_AVAILABLE:
        return jsonify({"error": "ML not available"}), 503
    
    results = {}
    
    # Train recommendation model
    results['recommendation_model'] = ml_engine.train_recommendation_model()
    
    # Train prediction model
    results['prediction_model'] = ml_engine.train_prediction_model()
    
    # Train engagement model
    results['engagement_model'] = ml_engine.train_engagement_model()
    
    return jsonify({
        "status": "All models trained successfully",
        "results": results
    })

if __name__ == '__main__':
    print("🚀 EcoLearn Email API Server Starting...")
    print(f"📧 Email: {SMTP_EMAIL}")
    print(f"🌐 Server: http://localhost:5000")
    print("\n⚠️  IMPORTANT: Update SMTP_EMAIL and SMTP_PASSWORD in this file")
    print("   Or set SMTP_EMAIL and SMTP_PASSWORD environment variables\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
