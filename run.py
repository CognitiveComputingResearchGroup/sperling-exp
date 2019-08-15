from experiments import Experiment1

# Create experiment
try:
    exp = Experiment1('config.yml')
except Exception as exc:
    print('Raised exception during initialization: ', exc)
    exit(1)

# Run experiment

# Save results
