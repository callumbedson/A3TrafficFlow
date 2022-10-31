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
import findRoute 
from datetime import datetime, timedelta
import math
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


def scats_volume(scatsId):
    lag = 4
    file1 = 'data/newTrain.csv'
    dfScats = pd.read_csv(file1, encoding='utf-8').fillna(0)
    scatsUnique = dfScats["SCATS"].unique().tolist()
    if scatsId in scatsUnique:
        _, _, X_test, y_test, scaler = process_data(file1, file1, lag, 2000) #Feeds in training data and scats location to get volume at certain scats site
        y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).reshape(1, -1)[0]
        y_preds = []

        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1]))
        predicted = load_model('model/my_model'+str(scatsId)+'.h5').predict(X_test)
        predicted = scaler.inverse_transform(predicted.reshape(-1, 1)).reshape(1, -1)[0]
        y_preds.append(predicted[:96])
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elapsed = now - midnight
        number_of_intervals = round(elapsed / timedelta(minutes=15)) - 1 #convert 15 minute time interval of current day to integer for index

        return predicted[number_of_intervals]

    else:
        print("Please enter a valid SCATS id contained in the dataset")
        return -1


def main(command):
    nCommand = command.split(" ")
    if nCommand[0] == "test":
        #test for SCATS 2000
        lstm = load_model('model/lstm2000.h5')
        gru = load_model('model/gru2000.h5')
        saes = load_model('model/saes2000.h5')
        my_model = load_model('model/my_model2000.h5')
        models = [lstm, gru, saes, my_model]
        names = ['LSTM', 'GRU', 'SAEs', 'My model']

        lag = 4
        file1 = 'data/newTrain.csv'
        dfScats = pd.read_csv(file1, encoding='utf-8').fillna(0)
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

    elif nCommand[0] == "exit":
        quit()

    elif nCommand[0] == "search":
        if len(nCommand) > 2:
            if nCommand[1].isnumeric() and nCommand[2].isnumeric():
                allRoutes = findRoute.main(nCommand[1], nCommand[2])
                sRoutes = []
                for x in range(len(allRoutes)):
                    time = 0
                    for y in range(len(allRoutes[x])):
                        q = scats_volume(int(allRoutes[x][y][0])) * 4 #volume for SCATS site A
                        qMax = 1000 #jam density assumed to be 66 for cars travelling 60km/h
                        uC = 32 # at capacity when speed is 32km/h
                        a = (-qMax/pow(uC,2))
                        b = -2 * uC * a
                        v = abs((math.sqrt(4*a*q+pow(b,2))+b)/2*a) #quadratic formula to find v from a, b and q

                        time += (allRoutes[x][y][2]/v)*60+0.5 #find time taken with speed and distance, and convert to minutes (+30 secs at SCATS intersection pass)

                    sRoutes.append((allRoutes[x], time))
            sRoutes.sort(key=lambda z: z[1])
            for x in range(len(sRoutes)):
                if x < 5:
                    print("    ----Route ", x + 1, "----    ")
                    for y in range(len(sRoutes[x][0])):
                        print(str(int(sRoutes[x][0][y][0])), " -> ", str(int(sRoutes[x][0][y][1])))
                    print("This route will take approximately ", sRoutes[x][1], " minutes")

            else:
                print("Please enter SCATS numbers")
        else:
            print("Please enter SCATS numbers")
    elif nCommand[0] == "scats":
        if len(nCommand) > 1:
            volume = scats_volume(int(nCommand[1]))
            if volume != -1:
                print("SCATS traffic volume at site " + nCommand[1] + " is " + str(volume) + " at " + str(datetime.now()))
        else:
            print("Please enter SCATS numbers")
    else:
        print("Please enter a valid command")


if __name__ == '__main__':
    while True:
        command = input("""Please enter a command:
        search <source number> <destination number> - Searches for a route from SCATS source to SCATS destination
        scats <number>
        test - Tests SCATS 2000 with all ML algorithms and displays comparisons
        exit - Closes the Bundoora SCATS search application\n>""")
        main(command)
