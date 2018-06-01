from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import tensorflow as tf
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', default=100, type=int, help='batch size')
parser.add_argument('--train_steps', default=1000, type=int,
                    help='number of training steps')

CSV_COLUMN_NAMES = ['Action', 'Comedy',
                    'Psycho', 'Score']


def input_evaluation_set():
    features = {'Very Good': np.array([10,9,8]),
                'Good':  np.array([7,6]),
                'Okay': np.array([5,4]),
                'Bad':  np.array([3,2,1])}
    labels = np.array([2, 1])
    return features, labels


def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    return dataset.shuffle(1000).repeat().batch(batch_size)


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


def load_data(y_name='Score'):
    """Returns the iris dataset as (train_x, train_y), (test_x, test_y)."""
    train_path, test_path = "game_dataset","test_game_dataset"

    train = pd.read_csv(train_path, names=CSV_COLUMN_NAMES, header=0)
    train_x, train_y = train, train.pop(y_name)

    test = pd.read_csv(test_path, names=CSV_COLUMN_NAMES, header=0)
    test_x, test_y = test, test.pop(y_name)

    return (train_x, train_y), (test_x, test_y)


def main(argv):
    args = parser.parse_args(argv[1:])

    # Fetch the data
    (train_x, train_y), (test_x, test_y) = load_data()
    my_feature_columns = []
    for key in train_x.keys():
        my_feature_columns.append(tf.feature_column.numeric_column(key=key))

    # classifier = tf.estimator.DNNClassifier(
    #     feature_columns=my_feature_columns,
    #     # Two hidden layers of 10 nodes each.
    #     hidden_units=[10, 10],
    #     # The model must choose between 3 classes.
    #     n_classes=120)

    estimator = tf.estimator.LinearRegressor(feature_columns=my_feature_columns)

    estimator.train(
        input_fn=lambda: train_input_fn(train_x,
                                        train_y, args.batch_size),
        steps=args.train_steps)
    eval_result = estimator.evaluate(
        input_fn=lambda: eval_input_fn(test_x, test_y, args.batch_size))
    # classifier.train(
    #     input_fn=lambda:train_input_fn(train_x,
    #         train_y, args.batch_size),
    #     steps=args.train_steps)

    # eval_result = classifier.evaluate(
    #     input_fn=lambda:eval_input_fn(test_x, test_y, args.batch_size))
    # print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**eval_result))
    print("Eval results", eval_result)
    # Generate predictions from the model
    expected = [40, 2, 15]
    predict_x = {
        'Action': [0, 1, 0],
        'Comedy': [1, 0, 0],
        'Psycho': [0, 1, 1]
    }

    # predictions = classifier.predict(
    #     input_fn=lambda:eval_input_fn(predict_x,expected,
    #                                         batch_size=args.batch_size))
    predictions = estimator.predict(
        input_fn=lambda: eval_input_fn(predict_x, expected,
                                       batch_size=args.batch_size))

    template = '\nPrediction is "{}" ({:.1f}%), expected "{}"'
    # print("predictions:", predictions.eval(),"\n expected:", expected)
    # for pred_dict, expec in zip(predictions, expected):
    #     class_id = 7
    #     # class_id = pred_dict['class_ids'][0]
    #     probability = pred_dict['probabilities'][class_id]
    #
    #     print(template.format(str(class_id),
    #                           100 * probability, expec))
    for i, prediction in enumerate(predictions):
        print(" ", prediction["predictions"][0])
    print()



if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(main)