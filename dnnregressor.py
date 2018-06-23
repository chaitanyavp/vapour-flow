"""Regression using the DNNRegressor Estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import numpy as np
import tensorflow as tf

STEPS = 5000
SCALE = 1000
train_fraction=0.7
# path = "genre_rating_categ.csv"
path = "steam_data.csv"
y_name = "Time"
data_from_path = None

# Order is important for the csv-readers, so we use an OrderedDict here.
defaults = collections.OrderedDict([
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
])  # pyformat: disable


types = collections.OrderedDict((key, type(value[0]))
                                for key, value in defaults.items())

CSV_COLUMN_NAMES = ['Action','Adventure','Casual','Indie', 'Massively_Multiplayer',
                    'Racing', 'RPG', 'Simulation','Sports', 'Strategy', 'Time']


def decode_line(line):
    """Convert a csv line into a (features_dict,label) pair."""
    # Decode the line to a tuple of items based on the types of
    # csv_header.values().
    items = tf.decode_csv(line, list(defaults.values()))

    # Convert the keys and items to a dict.
    pairs = zip(defaults.keys(), items)
    features_dict = dict(pairs)

    # Remove the label from the features_dict
    label = features_dict.pop(y_name)

    return features_dict, label


def in_training_set(line):
    """Returns a boolean tensor, true if the line is in the training set."""
    # If you randomly split the dataset you won't get the same split in both
    # sessions if you stop and restart training later. Also a simple
    # random split won't work with a dataset that's too big to `.cache()` as
    # we are doing here.
    bucket_id = tf.string_to_hash_bucket_fast(line, 1000000)
    # Use the hash bucket id as a random number that's deterministic per example
    return bucket_id < int(train_fraction * 1000000)


def from_list(list_of_lines):
    global data_from_path
    data_from_path = list_of_lines
    main([""])


def main(argv):
    """Builds, trains, and evaluates the model."""
    assert len(argv) == 1
    if data_from_path is None:
        base_dataset = (tf.data.TextLineDataset(path))
    else:
        base_dataset = data_from_path
    train = (base_dataset
           # Take only the training-set lines.
           .filter(in_training_set)
           # Decode each line into a (features_dict, label) pair.
           .map(decode_line)
           # Cache data so you only decode the file once.
           .cache())

    # Do the same for the test-set.
    test = (base_dataset.filter(lambda line: ~in_training_set(line)).cache().map(decode_line))

    # Switch the labels to units of thousands for better convergence.
    def scale_down(features, labels):
        return features, labels / SCALE

    train = train.map(scale_down)
    test = test.map(scale_down)

    # Build the training input_fn.
    def input_train():
        return (
            # Shuffling with a buffer larger than the data set ensures
            # that the examples are well mixed.
            train.shuffle(1000).batch(128)
            # Repeat forever
            .repeat().make_one_shot_iterator().get_next())


    # Build the validation input_fn.
    def input_test():
        return (test.shuffle(1000).batch(128)
                .make_one_shot_iterator().get_next())

    def eval_input_fn(features, labels, batch_size):
        """An input function for evaluation or prediction"""
        features=dict(features)
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

    # The first way assigns a unique weight to each category. To do this you must
    # specify the category's vocabulary (values outside this specification will
    # receive a weight of zero). Here we specify the vocabulary using a list of
    # options. The vocabulary can also be specified with a vocabulary file (using
    # `categorical_column_with_vocabulary_file`). For features covering a
    # range of positive integers use `categorical_column_with_identity`.
    body_style_vocab = ["True", "False"]
    feature_columns = []
    for col_name in CSV_COLUMN_NAMES[:-1]:
        feature_columns.append(tf.feature_column.indicator_column(
          tf.feature_column.categorical_column_with_vocabulary_list(key=col_name,
            vocabulary_list=body_style_vocab))
        )


    # Build a DNNRegressor, with 2x20-unit hidden layers, with the feature columns
    # defined above as input.
    model = tf.estimator.DNNRegressor(
      hidden_units=[20, 20], feature_columns=feature_columns)

    # Train the model.
    model.train(input_fn=input_train, steps=STEPS)

    # Evaluate how the model performs on data it has not yet seen.
    eval_result = model.evaluate(input_fn=input_test)

    # The evaluation returns a Python dictionary. The "average_loss" key holds the
    # Mean Squared Error (MSE).
    average_loss = eval_result["average_loss"]

    # Convert MSE to Root Mean Square Error (RMSE).
    print("\n" + 80 * "*")
    print("\nRMS error for the test set: {:.0f}"
        .format(SCALE * average_loss ** 0.5))

    print()

    predict_x = {
        'Action':    ["True", "False", "True"],
        'Adventure': ["False", "False", "True"],
        'Casual':    ["False", "False", "False"],
        'Indie':     ["True", "False", "False"],
        'Massively_Multiplayer': ["False", "False", "True"],
        'Racing':    ["False", "False", "False"],
        'RPG':       ["False", "False", "False"],
        'Simulation':["False", "False", "False"],
        'Sports':    ["False", "False", "False"],
        'Strategy':  ["False", "True", "False"]
    }

    # predictions = classifier.predict(
    #     input_fn=lambda:eval_input_fn(predict_x,expected,
    #                                         batch_size=batch_size))

    games = ["Cuphead", "Civ 6", "PUBG"]
    predictions = model.predict(
        input_fn=lambda: eval_input_fn(predict_x, None,
                                       batch_size=128))
    for i, prediction in enumerate(predictions):
        print(" ", games[i] + ": ", prediction["predictions"][0] * SCALE / 30, "hours")
        # print(" ", prediction["predictions"][0], "mins")
    print()

if __name__ == "__main__":
    # The Estimator periodically generates "INFO" logs; make these logs visible.
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main=main)
