"""Regression using the DNNRegressor Estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import numpy as np
import tensorflow as tf


class SteamDataRegressor:

    def __init__(self):
        self._steps = 5000
        self._scale = 1000
        self._train_fraction=0.7
        self._path = "steam_data.csv"
        self._y_name = "Time"

        self._defaults = collections.OrderedDict([
            ("Action", [""]),
            ("Adventure", [""]),
            ("Casual", [""]),
            ("Indie", [""]),
            ("Massively_Multiplayer", [""]),
            ("Racing", [""]),
            ("RPG", [""]),
            ("Simulation", [""]),
            ("Sports", [""]),
            ("Strategy", [""]),
            ("Time", [0.0])
        ])
        self._types = collections.OrderedDict((key, type(value[0]))
                                for key, value in self._defaults.items())
        self._csv_column_names = ['Action', 'Adventure', 'Casual', 'Indie',
                                  'Massively_Multiplayer', 'Racing', 'RPG',
                                  'Simulation', 'Sports', 'Strategy', 'Time']
        self._model = None

    def decode_line(self, line):
        """Convert a csv line into a (features_dict,label) pair."""
        # Decode the line to a tuple of items based on the types of
        # csv_header.values().
        items = tf.decode_csv(line, list(self._defaults.values()))

        # Convert the keys and items to a dict.
        pairs = zip(self._defaults.keys(), items)
        features_dict = dict(pairs)

        # Remove the label from the features_dict
        label = features_dict.pop(self._y_name)
        return features_dict, label

    def in_training_set(self, line):
        """Returns a boolean tensor, true if the line is in the training set."""
        bucket_id = tf.string_to_hash_bucket_fast(line, 1000000)
        # Use the hash bucket id as a random number that's deterministic per example
        return bucket_id < int(self._train_fraction * 1000000)

    def scale_down(self, features, labels):
        return features, labels / self._scale

    def create_model(self):
        category_vocab = ["True", "False"]
        feature_columns = []
        for col_name in self._csv_column_names[:-1]:
            feature_columns.append(tf.feature_column.indicator_column(
              tf.feature_column.categorical_column_with_vocabulary_list(
                  key=col_name, vocabulary_list=category_vocab))
            )
        # Build  DNNRegressor, with 2x20-unit hidden layers, with featurecolumns
        self._model = tf.estimator.DNNRegressor(
          hidden_units=[20, 20], feature_columns=feature_columns)

    def train_model(self, base_dataset):
        train = (base_dataset.filter(self.in_training_set).map(self.decode_line)
                 .cache())
        train = train.map(self.scale_down)

        def _train_helper():
            return (train.shuffle(1000).batch(128)
                    .repeat().make_one_shot_iterator().get_next())

        self._model.train(input_fn=_train_helper, steps=self._steps)

    def test_model(self, base_dataset):
        test = (base_dataset.filter(lambda line: ~self.in_training_set(line))
                .cache().map(self.decode_line))
        test = test.map(self.scale_down)

        def _test_helper():
            return (test.shuffle(1000).batch(128)
                    .make_one_shot_iterator().get_next())

        # Evaluate how the model performs on data it has not yet seen.
        eval_result = self._model.evaluate(input_fn=_test_helper)

        # The evaluation returns a Python dictionary. The "average_loss" key
        # holds the Mean Squared Error (MSE).
        average_loss = eval_result["average_loss"]
        # Convert MSE to Root Mean Square Error (RMSE).
        print("\n" + 80 * "*")
        print("\nRMS error for the test set: {:.0f}"
            .format(self._scale * average_loss ** 0.5))

        print()

    def make_prediction(self):
        predict_x = {
            'Action': ["False", "False", "True"],
            'Adventure': ["False", "False", "True"],
            'Casual': ["False", "False", "False"],
            'Indie': ["False", "False", "False"],
            'Massively_Multiplayer': ["False", "False", "True"],
            'Racing': ["False", "False", "False"],
            'RPG': ["True", "False", "False"],
            'Simulation': ["False", "False", "False"],
            'Sports': ["False", "False", "False"],
            'Strategy': ["False", "True", "False"]
        }

        games = ["Skyrim", "Civ 6", "PUBG"]

        def _eval_helper(features, labels, batch_size):
            """An input function for evaluation or prediction"""
            features = dict(features)
            if labels is None:
                # No labels, use only features.
                inputs = features
            else:
                inputs = (features, labels)

            # Convert the inputs to a Dataset.
            dataset = tf.data.Dataset.from_tensor_slices(inputs)

            # Batch the examples
            assert batch_size is not None, "batch_size must not be None"
            dataset = dataset.batch(batch_size)

            # Return the dataset.
            return dataset

        predictions = self._model.predict(
            input_fn=lambda: _eval_helper(predict_x, None,
                                          batch_size=128))
        for i, prediction in enumerate(predictions):
            print(" ", games[i] + ": ",
                  prediction["predictions"][0] * self._scale / 30, "hours")
            # print(" ", prediction["predictions"][0], "mins")
        print()

    def prepare_entire_model(self):
        self.create_model()
        base_dataset = (tf.data.TextLineDataset(self._path))
        self.train_model(base_dataset)
        self.test_model(base_dataset)

    def main(self, argv):
        """Builds, trains, and evaluates the model."""
        assert len(argv) == 1
        base_dataset = (tf.data.TextLineDataset(self._path))

        self.create_model()
        assert self._model is not None

        # Train the model.
        self.train_model(base_dataset)

        # Test the model
        self.test_model(base_dataset)

        self.make_prediction()

if __name__ == "__main__":
    # The Estimator periodically generates "INFO" logs; make these logs visible.
    reg = SteamDataRegressor()
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main=reg.main)
