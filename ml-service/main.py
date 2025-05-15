import os
import pickle
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Optional
import structlog
import redis
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from jose import JWTError, jwt
from passlib.context import CryptContext
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configure structured logging
logger = structlog.get_logger()

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Redis connection for rate limiting
redis_client = redis.Redis(
    host='redis',
    port=6379,
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

# Prometheus metrics
request_count = Counter('ml_api_requests_total', 'Total API requests', ['method', 'endpoint'])
prediction_time = Histogram('ml_prediction_seconds', 'Time spent on predictions')
prediction_count = Counter('ml_predictions_total', 'Total predictions made')

app = FastAPI(title="Secure ML API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dev.localhost"],  # Only allow dev environment
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class PredictionInput(BaseModel):
    features: List[float]
    
    @validator('features')
    def validate_features(cls, v):
        if len(v) != 4:
            raise ValueError('Iris dataset requires exactly 4 features')
        if any(f < 0 for f in v):
            raise ValueError('Feature values must be positive')
        return v

class PredictionOutput(BaseModel):
    prediction: int
    probability: List[float]
    model_version: str
    timestamp: str

# Model management
class ModelManager:
    def __init__(self):
        self.model = None
        self.model_hash = None
        self.model_version = "1.0.0"
        self.load_or_train_model()
    
    def load_or_train_model(self):
        """Load existing model or train new one with data integrity checks"""
        model_path = "/app/models/iris_model.pkl"
        
        if os.path.exists(model_path):
            # Load existing model with integrity check
            with open(model_path, 'rb') as f:
                model_data = f.read()
                
            # Verify model hash
            current_hash = hashlib.sha256(model_data).hexdigest()
            
            try:
                with open(f"{model_path}.hash", 'r') as f:
                    stored_hash = f.read().strip()
                
                if current_hash != stored_hash:
                    logger.warning("Model hash mismatch, retraining model")
                    self.train_model()
                else:
                    self.model = pickle.loads(model_data)
                    self.model_hash = current_hash
                    logger.info("Model loaded successfully", hash=current_hash)
            except FileNotFoundError:
                logger.warning("Hash file not found, retraining model")
                self.train_model()
        else:
            self.train_model()
    
    def train_model(self):
        """Train model with data validation and integrity measures"""
        logger.info("Training new model")
        
        # Load and validate data
        data = load_iris()
        X, y = data.data, data.target
        
        # Data validation
        if X.shape[1] != 4:
            raise ValueError("Invalid feature count in dataset")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=5  # Prevent overfitting
        )
        self.model.fit(X_train, y_train)
        
        # Validate model performance
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        if accuracy < 0.8:  # Minimum acceptable accuracy
            raise ValueError(f"Model accuracy too low: {accuracy}")
        
        # Save model with integrity hash
        os.makedirs("/app/models", exist_ok=True)
        model_path = "/app/models/iris_model.pkl"
        
        with open(model_path, 'wb') as f:
            model_data = pickle.dumps(self.model)
            f.write(model_data)
        
        # Save hash for integrity verification
        self.model_hash = hashlib.sha256(model_data).hexdigest()
        with open(f"{model_path}.hash", 'w') as f:
            f.write(self.model_hash)
        
        # Save model metadata
        metadata = {
            "version": self.model_version,
            "accuracy": accuracy,
            "created_at": datetime.utcnow().isoformat(),
            "hash": self.model_hash
        }
        
        with open("/app/models/model_metadata.json", 'w') as f:
            json.dump(metadata, f)
        
        logger.info("Model trained and saved", accuracy=accuracy, hash=self.model_hash)

# Initialize model manager
model_manager = ModelManager()

# Authentication functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token with proper error handling"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Rate limiting
async def rate_limit(user: str = Depends(verify_token)):
    """Implement rate limiting per user"""
    key = f"rate_limit:{user}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, 60, 1)  # 1 request per minute initially
    else:
        if int(current) >= 10:  # 10 requests per minute max
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        redis_client.incr(key)

# API endpoints
@app.post("/token", response_model=Token)
async def login():
    """Simple token endpoint - in production, implement proper user authentication"""
    # In production, validate user credentials here
    access_token = create_access_token(data={"sub": "demo_user"})
    logger.info("Token generated", user="demo_user")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model_manager.model is not None}

@app.post("/predict", response_model=PredictionOutput)
async def predict(
    input_data: PredictionInput,
    user: str = Depends(rate_limit)
):
    """Make prediction with security and monitoring"""
    request_count.labels(method="POST", endpoint="/predict").inc()
    
    with prediction_time.time():
        try:
            # Convert input to numpy array
            features = np.array(input_data.features).reshape(1, -1)
            
            # Make prediction
            prediction = model_manager.model.predict(features)[0]
            probabilities = model_manager.model.predict_proba(features)[0].tolist()
            
            prediction_count.inc()
            
            # Log prediction for audit
            logger.info(
                "Prediction made",
                user=user,
                prediction=int(prediction),
                model_version=model_manager.model_version,
                model_hash=model_manager.model_hash[:8]
            )
            
            return PredictionOutput(
                prediction=int(prediction),
                probability=probabilities,
                model_version=model_manager.model_version,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error("Prediction failed", error=str(e), user=user)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prediction failed"
            )

@app.get("/model/info")
async def model_info(user: str = Depends(verify_token)):
    """Get model information and metadata"""
    try:
        with open("/app/models/model_metadata.json", 'r') as f:
            metadata = json.load(f)
        return metadata
    except FileNotFoundError:
        return {"error": "Model metadata not found"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(
        "Request processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)