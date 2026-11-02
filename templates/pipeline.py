"""Copy into a trusted research checkout and replace example source ownership."""
from tools.research_pipeline import Component, Pipeline

pipeline = Pipeline((
    Component('model', 'model', 'Predict outputs'),
    Component('features', 'model.features', 'Extract features',
              sources=({'path':'features.py'},)),
    Component('decoder', 'model.decoder', 'Decode predictions',
              sources=({'path':'decoder.py'},), dependencies=('features',)),
))

# Execution is defined with normal Python functions / ZenML @step and @pipeline.
# Export intent only after review: pipeline.export('records/components.json').
# Add task-specific semantic assertions; generic structural contracts are insufficient.
