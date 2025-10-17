"""
Configuration centralisée pour le système de contrôle d'accès restaurant
Centralise tous les paramètres configurables de l'application
"""

import os
from datetime import datetime

class Config:
    """Configuration principale de l'application"""
    
    # === PARAMÈTRES GÉNÉRAUX ===
    APP_NAME = "Restaurant Access Control System"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "Limayrac Python Course"
    
    # === BASE DE DONNÉES ===
    DATABASE_FILE = "students.json"
    DATABASE_BACKUP_DIR = "backups"
    DATABASE_MAX_SIZE = 10_000_000  # 10MB limite avant alerte
    
    # === IMAGES ET MÉDIAS ===
    IMAGES_DIR = "images"
    IMAGE_MAX_SIZE = (800, 600)  # Taille max images étudiants
    IMAGE_QUALITY = 85  # Qualité JPEG (0-100)
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # === RECONNAISSANCE FACIALE ===
    FACE_RECOGNITION_TOLERANCE = 0.6  # Plus bas = plus strict
    FACE_DETECTION_MODEL = "hog"  # "hog" ou "cnn"
    MIN_FACE_SIZE = (50, 50)  # Taille minimum visage pixels
    MAX_FACES_PER_IMAGE = 1  # Une seule face autorisée par image
    
    # === CAMÉRA ===
    CAMERA_INDEX = 0  # Index caméra par défaut
    CAMERA_FPS = 30  # Images par seconde
    CAMERA_RESOLUTION = (640, 480)  # Résolution capture
    CAMERA_TIMEOUT = 5000  # Timeout connexion caméra (ms)
    
    # === INTERFACE UTILISATEUR ===
    WINDOW_SIZE = "1000x700"
    WINDOW_MIN_SIZE = (800, 600)
    THEME_PRIMARY = "#2E86AB"
    THEME_SECONDARY = "#A23B72"
    THEME_SUCCESS = "#28A745"
    THEME_DANGER = "#DC3545"
    THEME_WARNING = "#FFC107"
    THEME_BACKGROUND = "#F8F9FA"
    
    # === GESTION FINANCIÈRE ===
    DEFAULT_BALANCE = 50.0  # Solde initial étudiant
    MEAL_COST = 5.0  # Prix repas standard
    MIN_BALANCE_WARNING = 10.0  # Seuil alerte solde faible
    CURRENCY_SYMBOL = "€"
    
    # === SÉCURITÉ ===
    ADMIN_ACCOUNTS = {
        "admin": "restaurant123",
        "manager": "access456",
        "supervisor": "control789"
    }
    
    # Tentatives connexion maximum
    MAX_LOGIN_ATTEMPTS = 3
    LOGIN_TIMEOUT_MINUTES = 15
    
    # === LOGGING ===
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FILE = "app.log"
    LOG_MAX_SIZE = 1_000_000  # 1MB avant rotation
    LOG_BACKUP_COUNT = 5  # Nombre fichiers log gardés
    
    # === PERFORMANCE ===
    DATABASE_SAVE_DELAY = 1000  # ms délai sauvegarde batch
    FACE_CACHE_SIZE = 100  # Nombre encodages en cache
    MEMORY_WARNING_THRESHOLD = 80  # % RAM avant alerte
    
    # === MAINTENANCE ===
    BACKUP_RETENTION_DAYS = 30  # Durée conservation backups
    CLEANUP_INTERVAL_HOURS = 24  # Fréquence nettoyage auto
    
    @classmethod
    def ensure_directories(cls):
        """Créer les répertoires nécessaires s'ils n'existent pas"""
        directories = [
            cls.IMAGES_DIR,
            cls.DATABASE_BACKUP_DIR,
            "logs"
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
    
    @classmethod
    def get_backup_filename(cls):
        """Générer nom fichier backup avec timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"students_backup_{timestamp}.json"
    
    @classmethod
    def validate_config(cls):
        """Valider cohérence configuration"""
        errors = []
        
        # Vérifier valeurs numériques positives
        if cls.MEAL_COST <= 0:
            errors.append("MEAL_COST must be positive")
        
        if cls.DEFAULT_BALANCE < 0:
            errors.append("DEFAULT_BALANCE cannot be negative")
        
        if cls.FACE_RECOGNITION_TOLERANCE <= 0 or cls.FACE_RECOGNITION_TOLERANCE >= 1:
            errors.append("FACE_RECOGNITION_TOLERANCE must be between 0 and 1")
        
        # Vérifier résolution caméra
        if len(cls.CAMERA_RESOLUTION) != 2:
            errors.append("CAMERA_RESOLUTION must be tuple (width, height)")
        
        # Vérifier taille images
        if len(cls.IMAGE_MAX_SIZE) != 2:
            errors.append("IMAGE_MAX_SIZE must be tuple (width, height)")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
        
        return True

class DevelopmentConfig(Config):
    """Configuration pour développement"""
    LOG_LEVEL = "DEBUG"
    DATABASE_FILE = "students_dev.json"
    FACE_RECOGNITION_TOLERANCE = 0.8  # Plus permissif pour tests

class ProductionConfig(Config):
    """Configuration pour production"""
    LOG_LEVEL = "WARNING"
    FACE_RECOGNITION_TOLERANCE = 0.5  # Plus strict
    MAX_LOGIN_ATTEMPTS = 5

class TestConfig(Config):
    """Configuration pour tests"""
    DATABASE_FILE = "students_test.json"
    IMAGES_DIR = "test_images"
    LOG_LEVEL = "DEBUG"
    MEAL_COST = 1.0  # Prix réduit pour tests

# Configuration active selon environnement
import os
ENV = os.getenv('APP_ENV', 'development').lower()

if ENV == 'production':
    active_config = ProductionConfig
elif ENV == 'test':
    active_config = TestConfig
else:
    active_config = DevelopmentConfig

# Validation au chargement
active_config.validate_config()
active_config.ensure_directories()

# Export pour utilisation dans autres modules
__all__ = ['Config', 'active_config']