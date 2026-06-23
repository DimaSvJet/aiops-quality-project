import os
import pickle
from datetime import datetime


def main():
    print("Starting model retraining...")

    os.makedirs("model", exist_ok=True)

    model_object = {
        "model_type": "linear_mock_model",
        "coef": 2.0,
        "bias": 0.0,
        "created_at": datetime.utcnow().isoformat()
    }

    with open("model/model.pkl", "wb") as f:
        pickle.dump(model_object, f)

    with open("model/version.txt", "w", encoding="utf-8") as f:
        f.write(model_object["created_at"])

    print("Model saved to model/model.pkl")
    print("Retraining finished successfully.")


if __name__ == "__main__":
    main()
