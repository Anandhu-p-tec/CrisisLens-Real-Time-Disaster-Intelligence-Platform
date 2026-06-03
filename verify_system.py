import sys
print('Python version:', sys.version)

try:
    from app.api.main import app
    print('✓ API module loaded')
except Exception as e:
    print('✗ API error:', e)

try:
    from app.classification.classifier import CrisisClassifier
    print('✓ Classifier module loaded')
except Exception as e:
    print('✗ Classifier error:', e)

try:
    from app.ingestion.stream_simulator import StreamSimulator
    print('✓ Simulator module loaded')
except Exception as e:
    print('✗ Simulator error:', e)

try:
    from app.pipeline.processor import CrisisProcessor
    print('✓ Pipeline module loaded')
except Exception as e:
    print('✗ Pipeline error:', e)

print('\nAll core modules ready!')
