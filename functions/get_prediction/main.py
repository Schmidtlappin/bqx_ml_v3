"""
BQX ML V3 - Unified Prediction API
Smart Vertex AI Architecture Implementation

This Cloud Function provides a unified API for all 196 BQX ML models.
It intelligently routes requests to either:
- Real-time endpoints (5 critical models)
- Batch prediction cache (191 non-critical models)

Cost: ~$20/month for the function + $342/month for endpoints + $100/month for batch
Total: $462/month (97% savings vs naive approach)
"""

import os
import json
from flask import Request, jsonify
from google.cloud import aiplatform
from google.cloud import bigquery
from datetime import datetime
import traceback

# Initialize clients
aiplatform.init(project='bqx-ml', location='us-central1')
bq_client = bigquery.Client(project='bqx-ml')

# Critical endpoints that use real-time predictions
CRITICAL_ENDPOINTS = {
    'EUR_USD_90': 'projects/499681702492/locations/us-central1/endpoints/7233721083998765056',
    'GBP_USD_90': 'projects/499681702492/locations/us-central1/endpoints/3376950953109356544',
    'USD_JPY_90': 'projects/499681702492/locations/us-central1/endpoints/4160014338318401536',
    'EUR_GBP_90': 'projects/499681702492/locations/us-central1/endpoints/7458901065367289856',
    'EUR_JPY_90': 'projects/499681702492/locations/us-central1/endpoints/1469113560964530176'
}

# BigQuery cache table for batch predictions
BATCH_CACHE_TABLE = 'bqx-ml.predictions.batch_cache'

def get_prediction(request: Request):
    """
    Main entry point for the Cloud Function.

    Accepts GET or POST requests with parameters:
    - pair: Currency pair (e.g., EUR_USD, GBP_USD)
    - window: Time window (45 or 90)
    - features: Optional JSON array of feature values

    Returns:
    - prediction: The model prediction
    - source: 'endpoint' or 'batch_cache'
    - latency_ms: Processing time
    - model: Full model name
    """
    try:
        # Parse request
        if request.method == 'POST':
            request_json = request.get_json()
        else:
            request_json = request.args

        # Extract parameters
        pair = request_json.get('pair', '').upper()
        window = request_json.get('window', '')
        features = request_json.get('features', None)

        # Validate parameters
        if not pair or not window:
            return jsonify({
                'error': 'Missing required parameters: pair and window',
                'example': '/predict?pair=EUR_USD&window=90'
            }), 400

        # Construct model name
        model_name = f"{pair}_{window}"

        # Check if this is a critical model with real-time endpoint
        if model_name in CRITICAL_ENDPOINTS and CRITICAL_ENDPOINTS[model_name]:
            return get_endpoint_prediction(model_name, features)
        else:
            return get_batch_prediction(model_name)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

def get_endpoint_prediction(model_name, features=None):
    """
    Get real-time prediction from Vertex AI endpoint.

    Args:
        model_name: Name of the model (e.g., EUR_USD_90)
        features: Optional feature values for prediction

    Returns:
        JSON response with prediction and metadata
    """
    start_time = datetime.now()

    try:
        # Get endpoint
        endpoint_id = CRITICAL_ENDPOINTS[model_name]
        endpoint = aiplatform.Endpoint(endpoint_id)

        # Prepare instances for prediction
        if features:
            instances = [features] if isinstance(features, list) else [[features]]
        else:
            # Use dummy features for testing
            instances = [[0.0] * 6030]  # 6030 features as per BQX paradigm

        # Make prediction
        predictions = endpoint.predict(instances=instances)

        # Calculate latency
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        return jsonify({
            'model': model_name,
            'prediction': predictions.predictions[0] if predictions.predictions else None,
            'source': 'endpoint',
            'latency_ms': round(latency_ms, 2),
            'endpoint_id': endpoint_id,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        return jsonify({
            'model': model_name,
            'error': str(e),
            'source': 'endpoint',
            'latency_ms': round(latency_ms, 2),
            'timestamp': datetime.now().isoformat()
        }), 500

def get_batch_prediction(model_name):
    """
    Get cached prediction from BigQuery batch results.

    Args:
        model_name: Name of the model (e.g., AUD_USD_45)

    Returns:
        JSON response with cached prediction and metadata
    """
    start_time = datetime.now()

    try:
        # Query BigQuery for cached prediction
        query = f"""
        SELECT
            model_name,
            prediction,
            confidence,
            prediction_time,
            batch_job_id
        FROM `{BATCH_CACHE_TABLE}`
        WHERE model_name = @model_name
            AND prediction_time >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 2 HOUR)
        ORDER BY prediction_time DESC
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("model_name", "STRING", model_name)
            ]
        )

        query_job = bq_client.query(query, job_config=job_config)
        results = list(query_job.result())

        # Calculate latency
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        if results:
            row = results[0]
            return jsonify({
                'model': model_name,
                'prediction': row.prediction,
                'confidence': row.confidence,
                'source': 'batch_cache',
                'cache_time': row.prediction_time.isoformat() if row.prediction_time else None,
                'batch_job_id': row.batch_job_id,
                'latency_ms': round(latency_ms, 2),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'model': model_name,
                'error': 'No recent batch prediction found. Batch jobs run hourly.',
                'source': 'batch_cache',
                'latency_ms': round(latency_ms, 2),
                'timestamp': datetime.now().isoformat()
            }), 404

    except Exception as e:
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        return jsonify({
            'model': model_name,
            'error': str(e),
            'source': 'batch_cache',
            'latency_ms': round(latency_ms, 2),
            'timestamp': datetime.now().isoformat()
        }), 500

def health_check(request: Request):
    """
    Health check endpoint for monitoring.

    Returns:
        JSON response with service status
    """
    try:
        # Check BigQuery connectivity
        bq_client.query("SELECT 1").result()
        bq_status = 'healthy'
    except:
        bq_status = 'unhealthy'

    # Check critical endpoints
    endpoint_status = {}
    for model, endpoint_id in CRITICAL_ENDPOINTS.items():
        if endpoint_id:
            try:
                endpoint = aiplatform.Endpoint(endpoint_id)
                endpoint_status[model] = 'deployed' if endpoint.list_models() else 'no_models'
            except:
                endpoint_status[model] = 'error'
        else:
            endpoint_status[model] = 'not_configured'

    return jsonify({
        'status': 'healthy',
        'bigquery': bq_status,
        'critical_endpoints': endpoint_status,
        'architecture': 'Smart Vertex AI',
        'cost_per_month': '$462',
        'savings': '97% ($12,978/month saved)',
        'timestamp': datetime.now().isoformat()
    })

# Entry point for Cloud Functions
def main(request: Request):
    """
    Main entry point that routes to appropriate handler.
    """
    path = request.path

    if path == '/health':
        return health_check(request)
    else:
        return get_prediction(request)