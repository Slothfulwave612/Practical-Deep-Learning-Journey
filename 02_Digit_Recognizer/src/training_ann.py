"""
__author__: Anmol_Durgapal(@slothfulwave612)

Python module for training an Artificial Neural Network.
"""

# import necessary packages/modules
import numpy as np
import pandas as pd

import torch

from . import utils_class, utils_func

# defualt values
DEVICE = "cuda"
EPOCHS = 50
BATCH_SIZE = 275


def run_training(target, save_model=False):
    """
    Function to train ANN.

    Args:
        target (str): label column name.
        save_model (bool, optional): to save the model. Defaults to False.
    """

    # load the dataset
    train_df = pd.read_pickle("data/train.pkl")
    valid_df = pd.read_pickle("data/valid.pkl")
    test_df = pd.read_pickle("data/test.pkl")

    # split for training data
    X_train = train_df.drop(target, axis=1).to_numpy()
    y_train = train_df[target].to_numpy()

    # split for validation data
    X_valid = valid_df.drop(target, axis=1).to_numpy()
    y_valid = valid_df[target].to_numpy()

    # split for test data
    X_test = test_df.drop(target, axis=1).to_numpy()
    y_test = test_df[target].to_numpy()

    # init object of DigitDataset for train data-set
    train_dataset = utils_class.DigitDataset(
        features=X_train, target=y_train
    )

    # init object of DigitDataset for valid data-set
    valid_dataset = utils_class.DigitDataset(
        features=X_valid, target=y_valid
    )

    # init object of DigitDataset for valid data-set
    test_dataset = utils_class.DigitDataset(
        features=X_test, target=y_test
    )

    # create data loaders for train data set
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=BATCH_SIZE
    )

    # create data loaders for valid data set
    valid_loader = torch.utils.data.DataLoader(
        valid_dataset, batch_size=BATCH_SIZE
    )

    # create data loaders for test data set
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=BATCH_SIZE
    )

    # init object to make model
    model = utils_class.Model(
        num_features=X_train.shape[1],
        num_targets=10,
        num_layers=5,
        hidden_size=128,
        dropout=0.15
    )

    # transfer to GPU
    model = model.to(DEVICE)

    # make an optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # init object of Engine class
    engine = utils_class.Engine_ann(model, optimizer, DEVICE)

    # init a best loss
    best_loss = np.inf

    # init early stopping iter and counter
    early_stopping_iter, early_stopping_counter = 10, 0

    # init empty list for loss and accuracy
    loss_list_train, acc_list_train = [], []
    loss_list_valid, acc_list_valid = [], []

    for epoch in range(EPOCHS):
        # train and valid loss and accuracy
        train_loss, train_acc = engine.train(train_loader)
        valid_loss, valid_acc = engine.evaluate(valid_loader)

        # append the info
        loss_list_train.append(train_loss)
        loss_list_valid.append(valid_loss)
        acc_list_train.append(train_acc)
        acc_list_valid.append(valid_acc)

        print(f"Epoch: {epoch}:")
        print(f"Train Loss: {train_loss}, Valid Loss: {valid_loss}")
        print(f"Train Acc: {train_acc}, Valid Acc: {valid_acc}")
        print()

        # update the loss
        if valid_loss < best_loss:
            best_loss = valid_loss

            if save_model:
                torch.save(model.state_dict(), f"model_{epoch}.pt")

        else:
            early_stopping_counter += 1

        if early_stopping_counter == early_stopping_iter:
            break

    # test loss and accuracy
    test_loss, test_acc = engine.evaluate(test_loader)
    print(f"Test Loss: {test_loss}, Test Acc: {test_acc}")

    fig, ax = utils_func.plot_over_epochs(
        acc_list_train, acc_list_valid,
        "Accuracy Results", "Accuracy",
        "plots/ann_accuracy.jpg"
    )

    fig, ax = utils_func.plot_over_epochs(
        loss_list_train, loss_list_valid,
        "Loss Results", "Loss",
        "plots/ann_loss.jpg"
    )


if __name__ == "__main__":
    torch.manual_seed(42)
    run_training("label")
