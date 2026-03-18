"""
Deep Learning Machine Recommendation System
Uses neural networks to predict user skill level and recommend appropriate machines
"""
import os
import json
from datetime import datetime
from django.conf import settings

# Try to import TensorFlow, fall back to simple version if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("NumPy not available, using simplified ML model")

try:
    if HAS_NUMPY:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers, models, regularizers
        from tensorflow.keras.utils import to_categorical
        HAS_TENSORFLOW = True
    else:
        HAS_TENSORFLOW = False
except ImportError:
    HAS_TENSORFLOW = False
    print("TensorFlow not available, using simplified ML model")

from api.models import Machine, MachineSubmission, UserProfile
from django.contrib.auth.models import User


class DeepLearningRecommender:
    """
    Deep Learning based recommender system for machines
    Uses neural networks to predict user skill and recommend machines
    """
    
    # Feature categories for one-hot encoding
    DIFFICULTY_MAP = {'easy': 0, 'medium': 1, 'hard': 2, 'insane': 3}
    CATEGORY_KEYWORDS = {
        'web': ['web', 'http', 'sql', 'xss', 'html', 'php'],
        'pwn': ['pwn', 'buffer', 'overflow', 'bof', 'rop'],
        'crypto': ['crypto', 'rsa', 'aes', 'cipher', 'hash'],
        'forensics': ['forensic', 'memory', 'disk', 'steg', 'volatility'],
        'network': ['network', 'sniff', 'packet', 'wireshark'],
        'reverse': ['reverse', 'binary', 'debug', 'gdb', 'ida'],
        'os': ['linux', 'windows', 'macos', ' Privilege Escalation'],
        'misc': ['misc', 'quiz', 'challenge']
    }
    
    def __init__(self, model_path=None):
        self.model = None
        self.is_trained = False
        self.model_path = model_path or os.path.join(settings.MEDIA_ROOT, 'ml_models', 'recommender_model')
        self.feature_dim = self._get_feature_dim()
        
        if HAS_TENSORFLOW:
            self._load_model()
    
    def _get_feature_dim(self):
        """Calculate feature dimension"""
        difficulty_features = len(self.DIFFICULTY_MAP)  # 4
        category_features = len(self.CATEGORY_KEYWORDS)  # 8
        user_history_features = 10  # Last 10 machines attempted
        skill_features = 5  # Skill level features
        return difficulty_features + category_features + user_history_features + skill_features
    
    def _extract_machine_features(self, machine):
        """Extract features from a machine"""
        features = np.zeros(self.feature_dim)
        
        # Difficulty (one-hot)
        diff_idx = self.DIFFICULTY_MAP.get(machine.difficulty.lower() if hasattr(machine, 'difficulty') else 'medium', 1)
        features[diff_idx] = 1
        
        # Category (keyword-based)
        name_lower = machine.name.lower()
        desc_lower = machine.description.lower() if hasattr(machine, 'description') else ''
        
        cat_start = len(self.DIFFICULTY_MAP)
        for i, (category, keywords) in enumerate(self.CATEGORY_KEYWORDS.items()):
            if any(kw in name_lower or kw in desc_lower for kw in keywords):
                features[cat_start + i] = 1
        
        # Rating feature (normalized)
        rating_idx = cat_start + len(self.CATEGORY_KEYWORDS)
        if hasattr(machine, 'rating') and machine.rating:
            features[rating_idx] = min(machine.rating / 5.0, 1.0)
        
        return features
    
    def _extract_user_features(self, user):
        """Extract user skill features"""
        features = np.zeros(5)
        
        try:
            profile = user.profile
            points = profile.points
            
            # Points-based skill level (0-4)
            if points >= 10000:
                features[0] = 1.0  # Elite
            elif points >= 5000:
                features[0] = 0.75  # Pro
            elif points >= 2000:
                features[0] = 0.5  # Hacker
            elif points >= 500:
                features[0] = 0.25  # Script Kiddie
            else:
                features[0] = 0.1  # Newbie
            
            # Completion rate
            total_machines = Machine.objects.count()
            if total_machines > 0:
                completed = len(profile.completed_machines) if profile.completed_machines else 0
                features[1] = completed / total_machines
            
            # Rank encoding
            rank_map = {'Newbie': 0, 'Script Kiddie': 0.25, 'Hacker': 0.5, 'Pro Hacker': 0.75, 'Elite Hacker': 1.0}
            features[2] = rank_map.get(profile.rank, 0)
            
            # Frames unlocked (indicates experience)
            unlocked = len(profile.unlocked_frames) if profile.unlocked_frames else 0
            features[3] = min(unlocked / 6.0, 1.0)
            
            # Recent activity (higher = more active)
            recent_subs = MachineSubmission.objects.filter(user=user).order_by('-submitted_at')[:10].count()
            features[4] = min(recent_subs / 10.0, 1.0)
            
        except UserProfile.DoesNotExist:
            pass
        
        return features
    
    def _get_user_machine_history(self, user, num_machines=10):
        """Get user's machine history as features"""
        features = np.zeros(num_machines * 2)  # Machine ID + completion status
        
        submissions = MachineSubmission.objects.filter(user=user).order_by('-submitted_at')[:num_machines]
        
        for i, sub in enumerate(submissions):
            if i >= num_machines:
                break
            features[i * 2] = sub.machine_id / 1000.0  # Normalized machine ID
            features[i * 2 + 1] = 1.0 if sub.flag_type in ['user', 'root'] else 0.5
        
        return features
    
    def build_model(self):
        """Build the neural network model"""
        if not HAS_TENSORFLOW:
            return None
        
        model = models.Sequential([
            # Input layer
            layers.Input(shape=(self.feature_dim,)),
            
            # First hidden layer
            layers.Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Second hidden layer
            layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Third hidden layer
            layers.Dense(32, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer - predict skill level (0-1)
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def train(self, epochs=50, batch_size=32):
        """Train the model on user submission data"""
        if not HAS_TENSORFLOW:
            return {'status': 'skipped', 'message': 'TensorFlow not available'}
        
        # Collect training data
        X_train = []
        y_train = []
        
        users = User.objects.filter(profile__isnull=False)
        
        for user in users:
            try:
                profile = user.profile
                
                # Get user's completed machines
                submissions = MachineSubmission.objects.filter(user=user, flag_type__in=['user', 'root'])
                
                for sub in submissions:
                    machine = sub.machine
                    
                    # Create feature vector
                    features = np.zeros(self.feature_dim)
                    
                    # Machine features
                    machine_features = self._extract_machine_features(machine)
                    features[:len(machine_features)] = machine_features
                    
                    # User features
                    user_features = self._extract_user_features(user)
                    user_feat_start = self.feature_dim - 5 - 20  # Leave space for history
                    features[user_feat_start:user_feat_start + 5] = user_features
                    
                    # Target: success rate (1.0 for completed)
                    target = 1.0
                    
                    X_train.append(features)
                    y_train.append(target)
                    
            except Exception as e:
                continue
        
        if len(X_train) < 10:
            return {'status': 'insufficient_data', 'message': 'Not enough training data'}
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Build and train model
        self.build_model()
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        self.is_trained = True
        
        # Save model
        self._save_model()
        
        return {
            'status': 'success',
            'samples': len(X_train),
            'final_loss': float(history.history['loss'][-1]),
            'final_mae': float(history.history['mae'][-1])
        }
    
    def predict_skill_level(self, user):
        """Predict user's current skill level (0-1)"""
        if not HAS_TENSORFLOW or not self.model:
            # Fallback to simple calculation
            try:
                profile = user.profile
                points = profile.points
                if points >= 10000:
                    return 0.9
                elif points >= 5000:
                    return 0.7
                elif points >= 2000:
                    return 0.5
                elif points >= 500:
                    return 0.3
                return 0.1
            except:
                return 0.3
        
        features = self._create_user_feature_vector(user)
        prediction = self.model.predict(features, verbose=0)
        return float(prediction[0][0])
    
    def recommend_machines(self, user, limit=5):
        """
        Get deep learning powered machine recommendations
        Returns machines sorted by predicted suitability
        """
        # Get completed machines
        try:
            profile = user.profile
            completed_ids = set(profile.completed_machines or [])
        except UserProfile.DoesNotExist:
            completed_ids = set()
        
        # Get all incomplete machines
        available_machines = Machine.objects.exclude(id__in=completed_ids)
        
        if not available_machines.exists():
            return []
        
        # Get user's predicted skill level
        user_skill = self.predict_skill_level(user)
        
        # Score each machine
        recommendations = []
        
        for machine in available_machines:
            score = self._calculate_recommendation_score(machine, user_skill, user)
            recommendations.append({
                'machine': machine,
                'score': score,
                'reason': self._get_recommendation_reason(machine, user_skill)
            })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_recommendation_score(self, machine, user_skill, user):
        """Calculate recommendation score for a machine"""
        # Get machine difficulty (0-1 scale)
        diff_map = {'easy': 0.25, 'medium': 0.5, 'hard': 0.75, 'insane': 1.0}
        machine_diff = diff_map.get(machine.difficulty.lower() if hasattr(machine, 'difficulty') else 'medium', 0.5)
        
        # Skill match score (closer to user skill = better match)
        skill_match = 1 - abs(user_skill - machine_diff)
        
        # Rating bonus
        rating_bonus = (machine.rating or 0) / 20.0  # Max 0.25 bonus
        
        # Category familiarity bonus
        category_bonus = self._get_category_familiarity(machine, user)
        
        # Combined score
        score = (skill_match * 0.5) + (rating_bonus * 0.2) + (category_bonus * 0.3)
        
        return min(score, 1.0)
    
    def _get_category_familiarity(self, machine, user):
        """Calculate user's familiarity with machine category"""
        name_lower = machine.name.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in name_lower for kw in keywords):
                # Check if user has completed similar machines
                similar = Machine.objects.filter(name__icontains=keywords[0]).values_list('id', flat=True)
                completed = MachineSubmission.objects.filter(
                    user=user,
                    machine_id__in=similar,
                    flag_type__in=['user', 'root']
                ).count()
                
                if completed > 0:
                    return min(completed / 5.0, 1.0)
        
        return 0.3  # Default low familiarity
    
    def _get_recommendation_reason(self, machine, user_skill):
        """Generate human-readable recommendation reason"""
        diff_map = {'easy': 0.25, 'medium': 0.5, 'hard': 0.75, 'insane': 1.0}
        machine_diff = diff_map.get(machine.difficulty.lower() if hasattr(machine, 'difficulty') else 'medium', 0.5)
        
        diff = user_skill - machine_diff
        
        if diff > 0.3:
            return "Great for building confidence"
        elif diff > 0:
            return "Good progression challenge"
        elif diff > -0.2:
            return "Perfect skill match"
        else:
            return "Advanced challenge"
    
    def _create_user_feature_vector(self, user):
        """Create feature vector for a user"""
        features = np.zeros((1, self.feature_dim))
        
        # User features
        user_features = self._extract_user_features(user)
        user_feat_start = self.feature_dim - 5 - 20
        features[0, user_feat_start:user_feat_start + 5] = user_features
        
        # History features
        history = self._get_user_machine_history(user, 10)
        history_start = self.feature_dim - 20
        features[0, history_start:] = history
        
        return features
    
    def _save_model(self):
        """Save trained model to disk"""
        if self.model and HAS_TENSORFLOW:
            try:
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                self.model.save(self.model_path)
            except Exception as e:
                print(f"Could not save model: {e}")
    
    def _load_model(self):
        """Load trained model from disk"""
        if not HAS_TENSORFLOW:
            return
        
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                self.is_trained = True
        except Exception as e:
            print(f"Could not load model: {e}")
            self.build_model()


def get_deep_recommendations(user, limit=5):
    """
    Main function to get deep learning recommendations
    """
    recommender = DeepLearningRecommender()
    return recommender.recommend_machines(user, limit)


def train_deep_model(epochs=50):
    """
    Train the deep learning model
    """
    recommender = DeepLearningRecommender()
    return recommender.train(epochs=epochs)


def get_user_skill_prediction(user):
    """
    Get predicted skill level for a user
    """
    recommender = DeepLearningRecommender()
    return recommender.predict_skill_level(user)
