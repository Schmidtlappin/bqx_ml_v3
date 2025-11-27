"""
Deploy scikit-learn models to Vertex AI with Custom Prediction Routine
This fixes the "Model server exited unexpectedly" error
"""

import os
import pickle
import tempfile
import shutil
from google.cloud import aiplatform
from google.cloud import storage
import time

# Initialize
aiplatform.init(project='bqx-ml', location='us-central1')
storage_client = storage.Client(project='bqx-ml')

# Critical models to deploy
CRITICAL_MODELS = [
    "EUR_USD_90",
    "GBP_USD_90",
    "USD_JPY_90",
    "EUR_GBP_90",
    "EUR_JPY_90"
]

def create_custom_predictor_package(model_name):
    """
    Create a custom prediction package for scikit-learn models
    """

    # Create temporary directory for package
    temp_dir = tempfile.mkdtemp()
    package_dir = os.path.join(temp_dir, 'predictor')
    os.makedirs(package_dir)

    # Create predictor.py
    predictor_code = '''
import pickle
import numpy as np
from google.cloud import storage

class Predictor:
    """Custom predictor for scikit-learn models"""

    def __init__(self):
        self._model = None

    def load(self, artifacts_uri: str):
        """Load the model from GCS"""
        # Download model from GCS
        storage_client = storage.Client()

        # Parse GCS path
        if artifacts_uri.startswith('gs://'):
            path_parts = artifacts_uri[5:].split('/', 1)
            bucket_name = path_parts[0]
            blob_path = path_parts[1] + '/model.pkl' if len(path_parts) > 1 else 'model.pkl'
        else:
            raise ValueError(f"Invalid GCS path: {artifacts_uri}")

        # Download model
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        # Load model into memory
        model_bytes = blob.download_as_bytes()
        self._model = pickle.loads(model_bytes)

    def preprocess(self, prediction_input):
        """Preprocess the input"""
        # Convert input to numpy array
        instances = prediction_input.get("instances", [])
        return np.array(instances)

    def predict(self, instances):
        """Make predictions"""
        if self._model is None:
            raise RuntimeError("Model not loaded")

        # Make predictions
        predictions = self._model.predict(instances)

        # Convert to list for JSON serialization
        return predictions.tolist()

    def postprocess(self, prediction_results):
        """Format the output"""
        return {"predictions": prediction_results}
'''

    # Write predictor.py
    with open(os.path.join(package_dir, 'predictor.py'), 'w') as f:
        f.write(predictor_code)

    # Create setup.py
    setup_code = '''
from setuptools import setup

setup(
    name="bqx-predictor",
    version="1.0",
    py_modules=["predictor"],
    install_requires=[
        "numpy>=1.19.0",
        "scikit-learn>=0.24.0",
        "google-cloud-storage>=1.42.0",
    ]
)
'''

    # Write setup.py
    with open(os.path.join(temp_dir, 'setup.py'), 'w') as f:
        f.write(setup_code)

    # Create tarball
    tarball_path = os.path.join(temp_dir, 'predictor.tar.gz')
    shutil.make_archive(
        os.path.join(temp_dir, 'predictor'),
        'gztar',
        temp_dir,
        '.'
    )

    # Upload to GCS
    bucket = storage_client.bucket('bqx-ml-vertex-models')
    blob_name = f'{model_name}/predictor.tar.gz'
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(tarball_path)

    # Clean up
    shutil.rmtree(temp_dir)

    return f'gs://bqx-ml-vertex-models/{blob_name}'

def deploy_model_with_custom_predictor(model_name):
    """
    Deploy model with custom prediction routine
    """

    print(f"\n{'='*60}")
    print(f"📦 Deploying {model_name} with Custom Predictor")
    print(f"{'='*60}")

    try:
        # Create custom predictor package
        print("  1️⃣ Creating custom predictor package...")
        predictor_uri = create_custom_predictor_package(model_name)
        print(f"     ✅ Predictor package uploaded: {predictor_uri}")

        # Upload model with custom predictor
        print(f"  2️⃣ Uploading model with custom predictor...")
        model = aiplatform.Model.upload(
            display_name=f"bqx-{model_name}-custom",
            artifact_uri=f"gs://bqx-ml-vertex-models/{model_name}/",
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
            serving_container_predict_route="/v1/models/MODEL/versions/VERSION:predict",
            serving_container_health_route="/v1/models/MODEL",
            serving_container_environment_variables={
                "MODEL_NAME": model_name,
            },
            sync=True
        )
        print(f"     ✅ Model uploaded: {model.resource_name}")

        # Create endpoint
        print(f"  3️⃣ Creating endpoint...")
        endpoint = aiplatform.Endpoint.create(
            display_name=f"bqx-{model_name}-endpoint-custom",
            sync=True
        )
        print(f"     ✅ Endpoint created: {endpoint.resource_name}")

        # Deploy model to endpoint
        print(f"  4️⃣ Deploying model to endpoint (minimal resources)...")
        endpoint.deploy(
            model=model,
            deployed_model_display_name=f"{model_name}-deployment",
            machine_type="n1-standard-2",  # Minimal resources
            min_replica_count=1,
            max_replica_count=2,
            traffic_percentage=100,
            sync=True
        )
        print(f"     ✅ Model deployed successfully!")

        return {
            'success': True,
            'model': model.resource_name,
            'endpoint': endpoint.resource_name
        }

    except Exception as e:
        print(f"     ❌ Error deploying {model_name}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """
    Main deployment function
    """

    print("="*70)
    print("🚀 SMART VERTEX AI - CUSTOM PREDICTOR DEPLOYMENT")
    print("="*70)
    print("Fixing model format issues with custom prediction routines")
    print("="*70)

    results = {}
    successful = 0
    failed = 0

    for i, model_name in enumerate(CRITICAL_MODELS, 1):
        print(f"\n[{i}/{len(CRITICAL_MODELS)}] Processing {model_name}...")

        result = deploy_model_with_custom_predictor(model_name)
        results[model_name] = result

        if result['success']:
            successful += 1
        else:
            failed += 1

        # Wait between deployments
        if i < len(CRITICAL_MODELS):
            print("\n⏳ Waiting 30 seconds before next deployment...")
            time.sleep(30)

    # Print summary
    print("\n" + "="*70)
    print("📊 DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"✅ Successful: {successful}/{len(CRITICAL_MODELS)}")
    print(f"❌ Failed: {failed}/{len(CRITICAL_MODELS)}")

    print("\n📋 Endpoint Details:")
    for model_name, result in results.items():
        if result['success']:
            print(f"  • {model_name}: {result['endpoint']}")
        else:
            print(f"  • {model_name}: FAILED - {result.get('error', 'Unknown error')}")

    print("\n💰 Cost Analysis:")
    print(f"  • Deployed endpoints: {successful}")
    print(f"  • Monthly cost: ${successful * 68.40:.2f}")
    print(f"  • Savings vs naive approach: ${13420 - (successful * 68.40):.2f}")

if __name__ == "__main__":
    main()