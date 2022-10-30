"""
Traffic Flow Prediction with Neural Networks(SAEs、LSTM、GRU).
"""
import math
import warnings
import numpy as np
import pandas as pd
from data.data import process_data
from keras.models import load_model
from keras.utils.vis_utils import plot_model
import sklearn.metrics as metrics
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
warnings.filterwarnings("ignore")


def MAPE(y_true, y_pred):
    """Mean Absolute Percentage Error
    Calculate the mape.

    # Arguments
        y_true: List/ndarray, true data.
        y_pred: List/ndarray, predicted data.
    # Returns
        mape: Double, result data for train.
    """

    y = [x for x in y_true if x > 0]
    y_pred = [y_pred[i] for i in range(len(y_true)) if y_true[i] > 0]

    num = len(y_pred)
    sums = 0

    for i in range(num):
        tmp = abs(y[i] - y_pred[i]) / y[i]
        sums += tmp

    mape = sums * (100 / num)

    return mape


def eva_regress(y_true, y_pred):
    """Evaluation
    evaluate the predicted resul.

    # Arguments
        y_true: List/ndarray, ture data.
        y_pred: List/ndarray, predicted data.
    """

    mape = MAPE(y_true, y_pred)
    vs = metrics.explained_variance_score(y_true, y_pred)
    mae = metrics.mean_absolute_error(y_true, y_pred)
    mse = metrics.mean_squared_error(y_true, y_pred)
    r2 = metrics.r2_score(y_true, y_pred)
    print('explained_variance_score:%f' % vs)
    print('mape:%f%%' % mape)
    print('mae:%f' % mae)
    print('mse:%f' % mse)
    print('rmse:%f' % math.sqrt(mse))
    print('r2:%f' % r2)


def plot_results(y_true, y_preds, names):
    """Plot
    Plot the true data and predicted data.

    # Arguments
        y_true: List/ndarray, ture data.
        y_pred: List/ndarray, predicted data.
        names: List, Method names.
    """
    d = '2014-10-1 00:00'
    x = pd.date_range(d, periods=96, freq='15min')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(x, y_true, label='True Data')
    for name, y_pred in zip(names, y_preds):
        ax.plot(x, y_pred, label=name)

    plt.legend()
    plt.grid(True)
    plt.xlabel('Time of Day')
    plt.ylabel('Flow')

    date_format = mpl.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    plt.show()
    fig.savefig('images/eva.png')


def main(command):
    match command:
        case "test":
            lstm = load_model('model/lstm2000.h5')
            gru = load_model('model/gru2000.h5')
            saes = load_model('model/saes2000.h5')
            # my_model = load_model('model/my_model.h5')
            models = [lstm, gru, saes]
            names = ['LSTM', 'GRU', 'SAEs']

            lag = 4
            file1 = 'data/newTrain.csv'
            dfScats = pd.read_csv(file1, encoding='utf-8').fillna(0)
            scatsUnique = dfScats["SCATS"].unique().tolist()
            file2 = 'data/newTest.csv'
            _, _, X_test, y_test, scaler = process_data(file1, file2, lag, 2000)
            y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).reshape(1, -1)[0]

            y_preds = []
            for name, model in zip(names, models):
                if name == 'SAEs' or name == "My model":
                    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1]))
                else:
                    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
                file = 'images/' + name + '.png'
                plot_model(model, to_file=file, show_shapes=True)
                predicted = model.predict(X_test)
                predicted = scaler.inverse_transform(predicted.reshape(-1, 1)).reshape(1, -1)[0]
                y_preds.append(predicted[:96])
                print(name)
                eva_regress(y_test, predicted)

            plot_results(y_test[: 96], y_preds, names)

        case "exit":
            quit()

        case _:
            nCommand = command.split(" ")
            if nCommand[0] == "search":
                if len(nCommand) > 2:
                    if nCommand[1].isnumeric() and nCommand[2].isnumeric():
                        pass
                    else:
                        print("Please enter SCATS numbers")
                else:
                    print("Please enter SCATS numbers")
            if nCommand[0] == "scats":
                pass
            else:
                print("Please enter a valid command")


if __name__ == '__main__':
    while True:
        command = input("""Please enter a command:
        search <source number> <destination number> - Searches for a route from SCATS source to SCATS destination
            select <route number>: selects route number and displays information
            back - returns to home
        scats <number>
        test - Tests SCATS 2000 with all ML algorithms and displays comparisons
        exit - Closes the Bundoora SCATS search application\n>""")
        main(command)
