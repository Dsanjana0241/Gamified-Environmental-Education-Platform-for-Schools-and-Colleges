"""
EcoLearn ML Engine - Machine Learning Algorithms for Educational Analytics
============================================================================
ML Algorithms Implemented:
1. K-Means Clustering - User segmentation by learning behavior
2. Decision Tree - Learning path recommendation
3. Linear Regression - Performance prediction
4. Naive Bayes - Engagement classification
5. Collaborative Filtering - Content recommendation
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import json
import random
from datetime import datetime, timedelta

class EcoLearnMLEngine:
    """Main ML Engine for EcoLearn Platform"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.user_segments = None
        self.recommendation_model = None
        self.prediction_model = None
        self.engagement_model = None
        self.is_trained = False
        
    # ==================== 1. K-MEANS CLUSTERING ====================
    """
    Purpose: Segment users into learning behavior groups
    Algorithm: K-Means Clustering (Unsupervised Learning)
    Features: XP, Games Played, Lessons Completed, Login Frequency, Streak
    Output: 4 User Segments - Beginner, Regular, Active, Expert
    """
    
    def prepare_user_features(self, users_data):
        """Extract features from user data for clustering"""
        features = []
        user_ids = []
        
        for email, user in users_data.items():
            # Feature vector: [xp, games_played, lessons, streak, level]
            feature_vector = [
                user.get('xp', 0),
                user.get('gamesPlayed', 0),
                user.get('lessonsCompleted', 0),
                user.get('streak', 0),
                user.get('level', 1)
            ]
            features.append(feature_vector)
            user_ids.append(email)
            
        return np.array(features), user_ids
    
    def cluster_users(self, users_data, n_clusters=4):
        """K-Means Clustering for user segmentation"""
        if len(users_data) < n_clusters:
            return {"error": "Need at least 4 users for clustering"}
        
        features, user_ids = self.prepare_user_features(users_data)
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Apply K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_features)
        
        # Analyze clusters
        cluster_names = {
            0: "🌱 Beginner Learners",
            1: "📚 Regular Students", 
            2: "🔥 Active Warriors",
            3: "🏆 Eco Experts"
        }
        
        results = {
            "algorithm": "K-Means Clustering",
            "n_clusters": n_clusters,
            "silhouette_score": None,  # Could calculate if needed
            "clusters": {},
            "user_segments": {}
        }
        
        for i in range(n_clusters):
            cluster_users = [user_ids[j] for j in range(len(user_ids)) if clusters[j] == i]
            cluster_features = features[clusters == i]
            
            results["clusters"][i] = {
                "name": cluster_names.get(i, f"Cluster {i}"),
                "user_count": len(cluster_users),
                "users": cluster_users[:5],  # Show first 5
                "avg_xp": float(np.mean(cluster_features[:, 0])),
                "avg_games": float(np.mean(cluster_features[:, 1])),
                "avg_lessons": float(np.mean(cluster_features[:, 2])),
                "avg_streak": float(np.mean(cluster_features[:, 3]))
            }
            
            for user_id in cluster_users:
                results["user_segments"][user_id] = {
                    "cluster_id": i,
                    "segment_name": cluster_names.get(i, f"Cluster {i}")
                }
        
        self.user_segments = results["user_segments"]
        return results
    
    # ==================== 2. DECISION TREE RECOMMENDATION ====================
    """
    Purpose: Recommend learning content based on user profile
    Algorithm: Decision Tree Classifier (Supervised Learning)
    Input: User features (level, xp, preferences)
    Output: Recommended topic (Climate, Recycling, Ocean, Energy)
    """
    
    def train_recommendation_model(self, training_data=None):
        """Train Decision Tree for content recommendation"""
        # Generate synthetic training data if none provided
        if training_data is None:
            training_data = self._generate_synthetic_training_data()
        
        X = np.array([data['features'] for data in training_data])
        y = np.array([data['topic'] for data in training_data])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Decision Tree
        self.recommendation_model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.recommendation_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.recommendation_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.is_trained = True
        
        return {
            "algorithm": "Decision Tree Classifier",
            "accuracy": float(accuracy),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features": ["level", "xp", "games_played", "lessons", "climate_progress", "recycle_progress", "ocean_progress", "energy_progress"]
        }
    
    def recommend_topic(self, user_data):
        """Recommend learning topic for a user"""
        if not self.is_trained:
            self.train_recommendation_model()
        
        features = [
            user_data.get('level', 1),
            user_data.get('xp', 0) / 1000,  # Normalize
            user_data.get('gamesPlayed', 0),
            user_data.get('lessonsCompleted', 0),
            user_data.get('progress', {}).get('climate', 0) / 100,
            user_data.get('progress', {}).get('recycle', 0) / 100,
            user_data.get('progress', {}).get('ocean', 0) / 100,
            user_data.get('progress', {}).get('energy', 0) / 100
        ]
        
        prediction = self.recommendation_model.predict([features])[0]
        probabilities = self.recommendation_model.predict_proba([features])[0]
        
        topics = ['Climate', 'Recycling', 'Ocean', 'Energy']
        topic_probs = {topics[i]: float(probabilities[i]) for i in range(len(topics))}
        
        return {
            "recommended_topic": topics[prediction],
            "confidence": float(max(probabilities)),
            "all_probabilities": topic_probs,
            "reasoning": self._get_recommendation_reasoning(user_data, topics[prediction])
        }
    
    # ==================== 3. LINEAR REGRESSION PREDICTION ====================
    """
    Purpose: Predict user performance and learning completion
    Algorithm: Linear Regression (Supervised Learning)
    Input: Historical performance data
    Output: Predicted scores and completion time
    """
    
    def train_prediction_model(self, historical_data=None):
        """Train Linear Regression for performance prediction"""
        if historical_data is None:
            historical_data = self._generate_synthetic_performance_data()
        
        # Features: [hours_studied, games_played, current_level, avg_score]
        X = np.array([[d['hours'], d['games'], d['level'], d['avg_score']] for d in historical_data])
        y = np.array([d['next_score'] for d in historical_data])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.prediction_model = LinearRegression()
        self.prediction_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.prediction_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        return {
            "algorithm": "Linear Regression",
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "coefficients": self.prediction_model.coef_.tolist(),
            "intercept": float(self.prediction_model.intercept_)
        }
    
    def predict_performance(self, user_data, hours_next_week=5):
        """Predict user's next quiz score"""
        if self.prediction_model is None:
            self.train_prediction_model()
        
        # Calculate historical averages
        total_games = user_data.get('gamesPlayed', 0)
        total_score = user_data.get('totalScore', 0)
        avg_score = total_score / max(total_games, 1)
        
        features = [
            hours_next_week,
            total_games,
            user_data.get('level', 1),
            avg_score
        ]
        
        predicted_score = self.prediction_model.predict([features])[0]
        
        return {
            "predicted_next_score": max(0, int(predicted_score)),
            "current_average": round(avg_score, 2),
            "improvement_potential": round(predicted_score - avg_score, 2),
            "hours_recommended": hours_next_week,
            "model_confidence": "medium"  # Based on data size
        }
    
    # ==================== 4. NAIVE BAYES ENGAGEMENT ====================
    """
    Purpose: Classify user engagement level
    Algorithm: Gaussian Naive Bayes (Supervised Learning)
    Input: User activity features
    Output: Engagement level (Low, Medium, High)
    """
    
    def train_engagement_model(self):
        """Train Naive Bayes for engagement classification"""
        # Synthetic training data
        data = self._generate_engagement_training_data()
        
        X = np.array([d['features'] for d in data])
        y = np.array([d['engagement'] for d in data])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.engagement_model = GaussianNB()
        self.engagement_model.fit(X_train, y_train)
        
        y_pred = self.engagement_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return {
            "algorithm": "Gaussian Naive Bayes",
            "accuracy": float(accuracy),
            "classes": ["Low", "Medium", "High"]
        }
    
    def predict_engagement(self, user_data):
        """Predict user's engagement level"""
        if self.engagement_model is None:
            self.train_engagement_model()
        
        # Features: [days_since_last_login, avg_session_time, games_per_week, lessons_per_week]
        features = [
            user_data.get('days_since_login', 0),
            user_data.get('avg_session_minutes', 15),
            user_data.get('gamesPlayed', 0) / max(1, user_data.get('days_active', 1)) * 7,
            user_data.get('lessonsCompleted', 0) / max(1, user_data.get('days_active', 1)) * 7
        ]
        
        prediction = self.engagement_model.predict([features])[0]
        probabilities = self.engagement_model.predict_proba([features])[0]
        
        engagement_levels = ['Low', 'Medium', 'High']
        
        return {
            "engagement_level": engagement_levels[prediction],
            "confidence": float(max(probabilities)),
            "probabilities": {engagement_levels[i]: float(probabilities[i]) for i in range(3)},
            "recommendations": self._get_engagement_recommendations(engagement_levels[prediction])
        }
    
    # ==================== 5. COLLABORATIVE FILTERING ====================
    """
    Purpose: Recommend games based on similar users
    Algorithm: User-Based Collaborative Filtering
    """
    
    def collaborative_recommendations(self, user_email, all_users, n_recommendations=2):
        """Recommend games based on similar users"""
        if user_email not in all_users:
            return {"error": "User not found"}
        
        target_user = all_users[user_email]
        target_vector = self._get_user_preference_vector(target_user)
        
        similarities = []
        for email, user in all_users.items():
            if email != user_email:
                user_vector = self._get_user_preference_vector(user)
                similarity = self._cosine_similarity(target_vector, user_vector)
                similarities.append((email, similarity, user))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get games played by similar users but not by target
        target_games = set(target_user.get('games_history', []))
        recommendations = []
        
        for similar_user_email, similarity, user_data in similarities[:3]:
            user_games = set(user_data.get('games_history', []))
            new_games = user_games - target_games
            
            for game in new_games:
                if len(recommendations) < n_recommendations:
                    recommendations.append({
                        "game": game,
                        "recommended_by_similarity": round(similarity, 3),
                        "similar_user": similar_user_email
                    })
        
        return {
            "algorithm": "User-Based Collaborative Filtering",
            "similar_users_found": len(similarities),
            "top_similarity": round(similarities[0][1], 3) if similarities else 0,
            "recommendations": recommendations
        }
    
    # ==================== HELPER METHODS ====================
    
    def _generate_synthetic_training_data(self, n_samples=200):
        """Generate synthetic data for training"""
        data = []
        topics = [0, 1, 2, 3]  # Climate, Recycling, Ocean, Energy
        
        for _ in range(n_samples):
            level = random.randint(1, 10)
            xp = level * random.randint(50, 150)
            games = random.randint(0, 50)
            lessons = random.randint(0, 20)
            
            # Progress for each topic (0-100)
            climate = random.randint(0, 100)
            recycle = random.randint(0, 100)
            ocean = random.randint(0, 100)
            energy = random.randint(0, 100)
            
            # Determine topic based on lowest progress (recommend what they need)
            min_progress = min(climate, recycle, ocean, energy)
            if min_progress == climate:
                topic = 0
            elif min_progress == recycle:
                topic = 1
            elif min_progress == ocean:
                topic = 2
            else:
                topic = 3
            
            data.append({
                'features': [level, xp/1000, games, lessons, climate/100, recycle/100, ocean/100, energy/100],
                'topic': topic
            })
        
        return data
    
    def _generate_synthetic_performance_data(self, n_samples=100):
        """Generate synthetic performance data"""
        data = []
        for _ in range(n_samples):
            hours = random.uniform(1, 20)
            games = random.randint(0, 30)
            level = random.randint(1, 10)
            avg_score = random.uniform(50, 500)
            
            # Next score depends on hours studied and current performance
            next_score = avg_score + hours * 10 + games * 2 + random.uniform(-20, 20)
            
            data.append({
                'hours': hours,
                'games': games,
                'level': level,
                'avg_score': avg_score,
                'next_score': next_score
            })
        return data
    
    def _generate_engagement_training_data(self, n_samples=150):
        """Generate synthetic engagement data"""
        data = []
        for _ in range(n_samples):
            days_since = random.randint(0, 30)
            session_time = random.uniform(5, 60)
            games_per_week = random.uniform(0, 20)
            lessons_per_week = random.uniform(0, 10)
            
            # Determine engagement level
            if days_since > 7 or games_per_week < 2:
                engagement = 0  # Low
            elif days_since > 3 or games_per_week < 5:
                engagement = 1  # Medium
            else:
                engagement = 2  # High
            
            data.append({
                'features': [days_since, session_time, games_per_week, lessons_per_week],
                'engagement': engagement
            })
        return data
    
    def _get_user_preference_vector(self, user):
        """Get user's game preference vector"""
        games_played = user.get('games_history', [])
        all_games = ['quiz', 'recycling', 'runner', 'memory']
        vector = [1 if game in games_played else 0 for game in all_games]
        return vector
    
    def _cosine_similarity(self, v1, v2):
        """Calculate cosine similarity between two vectors"""
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        return dot / norm if norm != 0 else 0
    
    def _get_recommendation_reasoning(self, user_data, topic):
        """Generate human-readable reasoning for recommendation"""
        progress = user_data.get('progress', {})
        topic_progress = {
            'Climate': progress.get('climate', 0),
            'Recycling': progress.get('recycle', 0),
            'Ocean': progress.get('ocean', 0),
            'Energy': progress.get('energy', 0)
        }
        
        lowest_topic = min(topic_progress, key=topic_progress.get)
        
        if topic == lowest_topic:
            return f"Based on your progress, {topic} has the lowest completion ({topic_progress[topic]}%). We recommend focusing on this area."
        else:
            return f"Your learning pattern suggests interest in {topic}. Users similar to you excel in this topic."
    
    def _get_engagement_recommendations(self, level):
        """Get recommendations based on engagement level"""
        recommendations = {
            'Low': [
                "Set daily reminders to log in",
                "Start with 5-minute quick games",
                "Join the daily challenge"
            ],
            'Medium': [
                "Try new game modes",
                "Complete learning modules",
                "Compete on the leaderboard"
            ],
            'High': [
                "Explore advanced topics",
                "Help other learners",
                "Aim for all achievements"
            ]
        }
        return recommendations.get(level, [])
    
    # ==================== COMPREHENSIVE ANALYTICS ====================
    
    def generate_full_analytics(self, user_email, all_users):
        """Generate comprehensive ML analytics for a user"""
        if user_email not in all_users:
            return {"error": "User not found"}
        
        user = all_users[user_email]
        
        analytics = {
            "user_email": user_email,
            "timestamp": datetime.now().isoformat(),
            "ml_models": {}
        }
        
        # 1. User Clustering
        if len(all_users) >= 4:
            clustering_result = self.cluster_users(all_users)
            analytics["ml_models"]["user_clustering"] = clustering_result.get("user_segments", {}).get(user_email, {})
        
        # 2. Topic Recommendation
        rec_result = self.recommend_topic(user)
        analytics["ml_models"]["topic_recommendation"] = rec_result
        
        # 3. Performance Prediction
        pred_result = self.predict_performance(user)
        analytics["ml_models"]["performance_prediction"] = pred_result
        
        # 4. Engagement Prediction
        eng_result = self.predict_engagement(user)
        analytics["ml_models"]["engagement_analysis"] = eng_result
        
        # 5. Collaborative Recommendations
        if len(all_users) > 1:
            collab_result = self.collaborative_recommendations(user_email, all_users)
            analytics["ml_models"]["collaborative_filtering"] = collab_result
        
        # Overall ML Score
        analytics["ml_insights_summary"] = self._generate_insights_summary(analytics["ml_models"])
        
        return analytics
    
    def _generate_insights_summary(self, models):
        """Generate summary insights from all ML models"""
        summary = {
            "strengths": [],
            "areas_to_improve": [],
            "recommended_actions": []
        }
        
        # From engagement
        if 'engagement_analysis' in models:
            eng = models['engagement_analysis']
            if eng['engagement_level'] == 'High':
                summary["strengths"].append("High engagement level")
            elif eng['engagement_level'] == 'Low':
                summary["areas_to_improve"].append("Engagement level is low")
                summary["recommended_actions"].extend(eng.get('recommendations', []))
        
        # From recommendations
        if 'topic_recommendation' in models:
            rec = models['topic_recommendation']
            summary["recommended_actions"].append(f"Focus on {rec['recommended_topic']} topic")
        
        # From performance prediction
        if 'performance_prediction' in models:
            pred = models['performance_prediction']
            if pred['improvement_potential'] > 50:
                summary["strengths"].append("High improvement potential detected")
        
        return summary


# Create global instance
ml_engine = EcoLearnMLEngine()
