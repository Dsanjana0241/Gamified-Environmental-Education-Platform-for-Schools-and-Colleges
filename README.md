# 🌱 EcoLearn - Gamified Environmental Education Platform

A production-ready **Gamified Environmental Education Platform** with real-time email OTP authentication, interactive learning games, and progress tracking.

![EcoLearn Preview](https://img.shields.io/badge/Platform-Web-green)
![Flask](https://img.shields.io/badge/Backend-Flask-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🔐 Real-World Authentication
- **Email-based OTP verification** using Gmail SMTP
- Sign up with email verification
- Forgot password with OTP reset
- Secure session management
- 3-attempt limit for OTP

### 🎮 4 Interactive Learning Games
1. **🎯 Eco Quiz Challenge** - Test knowledge with explanations
2. **♻️ Recycling Master** - Match-3 with recycling facts
3. **🏃 Eco Runner Adventure** - Runner game with floating eco facts
4. **🧠 Green Memory** - Memory match with symbol learning

### 📚 Educational Content
- 6 Learning Modules (Climate, Recycling, Ocean, Energy, Forests, Water)
- Facts embedded in every game
- XP and coin rewards for learning
- Progress tracking for 4 environmental topics

### 🏆 Gamification
- XP system with levels
- Coin economy
- Achievement badges (12 to unlock)
- Daily challenges
- Global leaderboard
- Streak counter

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gmail account with App Password (for OTP emails)

### 1. Clone & Navigate
```bash
cd Gamified_environment
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Email (for OTP)
Edit `backend/app.py` and update these lines:
```python
SMTP_EMAIL = "your-email@gmail.com"        # Your Gmail
SMTP_PASSWORD = "your-app-password"        # Gmail App Password (16 characters)
```

**How to get Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Go to "App passwords"
4. Generate app password for "Mail"
5. Copy the 16-character password

### 4. Start Backend Server
```bash
python backend/app.py
```
Server runs on `http://localhost:5000`

### 5. Start Frontend
Open `frontend/index.html` directly in browser:
```bash
# OR use Python's simple server
python -m http.server 8080 --directory frontend
```
Then visit: `http://localhost:8080`

## 📁 Project Structure

```
Gamified-Environmental-Education-Platform-for-Schools-and-Colleges/
├── frontend/
│   └── index.html          # Main application (single-page)
├── backend/
│   ├── app.py              # Flask API with email OTP
│   └── ml_engine.py        # 🤖 ML Algorithms Engine
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 API Endpoints

### Authentication APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/send-otp` | POST | Send OTP to email |
| `/api/verify-otp` | POST | Verify OTP code |
| `/api/resend-otp` | POST | Resend new OTP |
| `/api/register` | POST | Create account |
| `/api/login` | POST | User login |
| `/api/reset-password` | POST | Reset password |
| `/api/health` | GET | Health check |

### 🤖 Machine Learning APIs
| Endpoint | Method | ML Algorithm | Purpose |
|----------|--------|--------------|---------|
| `/api/ml/status` | GET | - | Check ML system status |
| `/api/ml/user-clustering` | POST | K-Means Clustering | Segment users by behavior |
| `/api/ml/recommend-topic` | POST | Decision Tree | Recommend learning topics |
| `/api/ml/predict-performance` | POST | Linear Regression | Predict quiz scores |
| `/api/ml/predict-engagement` | POST | Naive Bayes | Classify engagement level |
| `/api/ml/collaborative-recommendations` | POST | Collaborative Filtering | Recommend games |
| `/api/ml/full-analytics` | POST | All Algorithms | Comprehensive ML analytics |
| `/api/ml/train-models` | POST | All Algorithms | Train/update ML models |

## 🎮 How to Use

### Sign Up
1. Click "Create Account"
2. Fill name, email, password
3. Check your email for OTP
4. Enter 6-digit code
5. Start learning!

### Play Games
- Navigate to **Games** tab
- Select any game
- Learn while playing!

### Track Progress
- View **Dashboard** for stats
- Check **Achievements** tab
- Complete daily challenges

## 🛠️ Technologies Used

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- CSS Grid & Flexbox
- CSS Animations & Transitions
- Web Audio API for sound effects
- localStorage for data persistence

### Backend
- Flask (Python)
- Flask-CORS for cross-origin
- smtplib (Gmail SMTP)
- email.mime for HTML emails

## 🔒 Security Features

- OTP expires after 10 minutes
- 3-attempt limit for OTP verification
- Password minimum 6 characters
- App Password protection (not regular password)
- HTTPS recommended for production

## 🤖 Machine Learning Integration

### Implemented ML Algorithms

#### 1. **K-Means Clustering** (Unsupervised Learning)
- **Purpose**: Segment users into 4 learning behavior groups
- **Features**: XP, Games Played, Lessons, Streak, Level
- **Output**: Beginner, Regular, Active, Expert segments
- **Endpoint**: `POST /api/ml/user-clustering`

#### 2. **Decision Tree Classifier** (Supervised Learning)
- **Purpose**: Recommend learning topics based on user profile
- **Input**: Level, XP, Progress in 4 topics
- **Output**: Recommended topic (Climate/Recycling/Ocean/Energy)
- **Endpoint**: `POST /api/ml/recommend-topic`

#### 3. **Linear Regression** (Supervised Learning)
- **Purpose**: Predict user's next quiz performance
- **Features**: Study hours, Games played, Current level, Avg score
- **Output**: Predicted score, Improvement potential
- **Endpoint**: `POST /api/ml/predict-performance`

#### 4. **Gaussian Naive Bayes** (Supervised Learning)
- **Purpose**: Classify user engagement level
- **Features**: Login frequency, Session time, Activity rate
- **Output**: Engagement level (Low/Medium/High)
- **Endpoint**: `POST /api/ml/predict-engagement`

#### 5. **Collaborative Filtering** (Recommendation System)
- **Purpose**: Recommend games based on similar users
- **Method**: User-based similarity (Cosine Similarity)
- **Output**: Games played by similar users
- **Endpoint**: `POST /api/ml/collaborative-recommendations`

### Using ML Features

1. **Train Models**: 
   ```bash
   curl -X POST http://localhost:5000/api/ml/train-models
   ```

2. **Get User Analytics**:
   ```bash
   curl -X POST http://localhost:5000/api/ml/full-analytics \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com"}'
   ```

3. **Get Topic Recommendation**:
   ```bash
   curl -X POST http://localhost:5000/api/ml/recommend-topic \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com"}'
   ```

## 🌟 Future Enhancements

- [x] 🤖 Machine Learning integration
- [ ] MongoDB/PostgreSQL database
- [ ] JWT token authentication
- [ ] Multiplayer games
- [ ] Video lessons
- [ ] Mobile app (React Native/Flutter)
- [ ] Deep Learning for content personalization

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Inspired by modern gamified learning platforms
- Built for environmental education awareness
- Perfect for schools, colleges, and eco-organizations

---

**Made with 💚 for a greener future!**
