import os
import pickle
import time
from datetime import datetime


class MockModel:
    def predict(self, value: float) -> float:
        return value * 2


def main():
    print("Starting model retraining...")
    time.sleep(2)

    model = MockModel()

    os.makedirs("model", exist_ok=True)

    model_path = "model/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    version_path = "model/version.txt"
    with open(version_path, "w", encoding="utf-8") as f:
        f.write(datetime.utcnow().isoformat())

    print(f"Model saved to {model_path}")
    print("Retraining finished successfully.")


if __name__ == "__main__":
    main()
