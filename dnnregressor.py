"""Regression using the DNNRegressor Estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import imports_steam as imports85  # pylint: disable=g-bad-import-order

STEPS = 5000
PRICE_NORM_FACTOR = 1000

CSV_COLUMN_NAMES = ['Action','Adventure','Casual','Indie', 'Massively_Multiplayer',
                    'Racing', 'RPG', 'Simulation','Sports', 'Strategy', 'Time']

def main(argv):
  """Builds, trains, and evaluates the model."""
  assert len(argv) == 1
  (train, test) = imports85.dataset()

  # Switch the labels to units of thousands for better convergence.
  def normalize_price(features, labels):
    return features, labels / PRICE_NORM_FACTOR

  train = train.map(normalize_price)
  test = test.map(normalize_price)

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
        .format(PRICE_NORM_FACTOR * average_loss**0.5))

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
    print(" ", games[i] + ": ", prediction["predictions"][0]*PRICE_NORM_FACTOR/20, "hours")
    # print(" ", prediction["predictions"][0], "mins")
  print()

if __name__ == "__main__":
  # The Estimator periodically generates "INFO" logs; make these logs visible.
  tf.logging.set_verbosity(tf.logging.INFO)
  tf.app.run(main=main)
