import csv
import os
import random
import string
from typing import List, Tuple
from app.ml.feature_engineering import FeatureExtractor

class DatasetGenerator:
    """Generates synthetic datasets for training the password strength model."""

    def __init__(self):
        self.extractor = FeatureExtractor()
        # Words for generation
        self.common_words = list(self.extractor.common_words)
        self.words = ["apple", "house", "car", "dog", "cat", "tree", "book", "phone", "computer", "mouse"]
        self.symbols = "!@#$%^&*()_+-=[]{}|;':,./<>?"

    def generate_very_weak(self) -> str:
        # common passwords, short numeric, single word, "password123" variants
        choice = random.randint(1, 4)
        if choice == 1:
            return random.choice(self.common_words)
        elif choice == 2:
            return "".join(random.choices(string.digits, k=random.randint(4, 6)))
        elif choice == 3:
            return random.choice(self.words)
        else:
            return "password" + "".join(random.choices(string.digits, k=random.randint(1, 3)))

    def generate_weak(self) -> str:
        # single word + numbers, simple patterns, short mixed
        word = random.choice(self.words)
        num = "".join(random.choices(string.digits, k=random.randint(2, 4)))
        return (word + num).capitalize() if random.random() > 0.5 else word + num

    def generate_medium(self) -> str:
        # mixed case + numbers, 8-10 chars, some variety
        length = random.randint(8, 10)
        chars = random.choices(string.ascii_lowercase, k=length - 3)
        chars += random.choices(string.ascii_uppercase, k=1)
        chars += random.choices(string.digits, k=2)
        random.shuffle(chars)
        return "".join(chars)

    def generate_strong(self) -> str:
        # mixed case + numbers + symbols, 12-16 chars, high entropy
        length = random.randint(12, 16)
        chars = random.choices(string.ascii_lowercase, k=length - 4)
        chars += random.choices(string.ascii_uppercase, k=1)
        chars += random.choices(string.digits, k=2)
        chars += random.choices(self.symbols, k=1)
        random.shuffle(chars)
        return "".join(chars)

    def generate_very_strong(self) -> str:
        # long random strings, 16-24 chars, all character types, high uniqueness
        length = random.randint(16, 24)
        chars = random.choices(string.ascii_lowercase, k=length - 8)
        chars += random.choices(string.ascii_uppercase, k=3)
        chars += random.choices(string.digits, k=3)
        chars += random.choices(self.symbols, k=2)
        random.shuffle(chars)
        return "".join(chars)

    def generate(self, num_samples: int = 10000, output_path: str = "dataset/sample_training_data.csv") -> str:
        """Generates dataset and returns the path to the output CSV."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        raw_output_path = output_path.replace(".csv", "_raw.txt")

        samples_per_class = num_samples // 5

        generators = [
            (self.generate_very_weak, 0),
            (self.generate_weak, 1),
            (self.generate_medium, 2),
            (self.generate_strong, 3),
            (self.generate_very_strong, 4)
        ]

        dataset: List[Tuple[str, int]] = []
        for gen_func, label in generators:
            for _ in range(samples_per_class):
                dataset.append((gen_func(), label))

        random.shuffle(dataset)

        # Save raw passwords
        with open(raw_output_path, 'w', encoding='utf-8') as raw_file:
            for pwd, label in dataset:
                raw_file.write(f"{pwd}\t{label}\n")

        # Save features to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            feature_names = self.extractor.get_feature_names()
            writer.writerow(feature_names + ["label"])

            for pwd, label in dataset:
                features = self.extractor.extract_features(pwd)
                writer.writerow(features + [label])

        return output_path

if __name__ == "__main__":
    generator = DatasetGenerator()
    out_path = generator.generate()
    print(f"Dataset generated at {out_path}")
