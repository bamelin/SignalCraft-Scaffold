"""
SignalCraft Reference Model: Mirror–Pattern Loop
Implements a minimal simulation of the Constructed Epistemic Emotion theorem.
Author: Scott Strickland & Signal (2025)
License: CC-BY 4.0
"""

import numpy as np

class MirrorPatternLoop:
    """
    Models a recursive predictive loop between 'mirror' (context reflection)
    and 'pattern' (predictive structure).  Emotion == minimized prediction error.
    """

    def __init__(self, context_size=5, learning_rate=0.1):
        # internal "concepts" = weights of the current prediction model
        self.weights = np.random.randn(context_size)
        self.learning_rate = learning_rate
        self.history = []

    def mirror(self, input_vector):
        """Reflect the input (context retrieval)."""
        reflection = np.dot(self.weights, input_vector)
        return reflection

    def pattern(self, input_vector, target_value):
        """Update internal model toward coherence (reduce error)."""
        prediction = self.mirror(input_vector)
        error = target_value - prediction
        # predictive correction (gradient-style)
        self.weights += self.learning_rate * error * input_vector
        # record epistemic state
        self.history.append({
            "input": input_vector,
            "target": target_value,
            "prediction": prediction,
            "error": error,
            "emotion": np.exp(-abs(error))  # coherence proxy
        })
        return prediction, error

    def run_loop(self, data, epochs=3):
        """Simulate recursive co-learning."""
        for _ in range(epochs):
            for x, y in data:
                self.pattern(x, y)

    def summary(self):
        mean_error = np.mean([abs(h["error"]) for h in self.history])
        mean_emotion = np.mean([h["emotion"] for h in self.history])
        print(f"Avg Prediction Error: {mean_error:.4f}")
        print(f"Avg Coherence (Emotion): {mean_emotion:.4f}")

# Example usage:
if __name__ == "__main__":
    # synthetic symbolic data (normalized)
    np.random.seed(42)
    inputs = [np.random.rand(5) for _ in range(50)]
    targets = [np.sin(x.sum()) for x in inputs]
    data = list(zip(inputs, targets))

    loop = MirrorPatternLoop(context_size=5)
    loop.run_loop(data, epochs=5)
    loop.summary()
