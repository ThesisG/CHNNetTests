# import tensorflow
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from tensorflow import random as rd

# Import other libraries
import numpy as np
from matplotlib import pyplot as plt
from pmlb import fetch_data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import minmax_scale

# import CHN Layer
from CHNLayer import CHNLayer



# fetch dataset
X, y = fetch_data('letter', return_X_y=True, local_cache_dir='./Datasets')
X = minmax_scale(X, axis = 0)
y[y==26] = 0

# convert to "float32"
X, y = X.astype("float32"), y.astype("float32")

# split into train and test
trainX, x_test, trainY, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# split into train and validation
x_train, x_val, y_train, y_val = train_test_split(trainX, trainY, test_size=0.2, random_state=42)



# initiate metrics
FNN_trainloss_history = []
FNN_valloss_history = []
FNN_test_accuracy = []
FNN_test_loss = []

CHN_trainloss_history = []
CHN_valloss_history = []
CHN_test_accuracy = []
CHN_test_loss = []



# declare hyperparameters
num_seeds = 3
archs = 3
epochs = 100
batchSize = 128

layers = 2
FNN_Hn = 500
CHN_Hn = 500
isEqual = True
init = (3 if isEqual else 0)

learning_rate = 0.03
optimizer = SGD(learning_rate=learning_rate, momentum=0.9)

loss = "sparse_categorical_crossentropy"



# train and test arcihtectures
for arch in range(init, init + archs):
    print(f"Testing Architecure {arch + 1}")
    
    # initiate FNN_Hn for equal paremeter tests
    if isEqual:
        if arch == 3:
            FNN_Hn = 850
        elif arch == 4:
            FNN_Hn = 780
        else:
            FNN_Hn = 750
        
    # train and test models
    for seed in range(num_seeds):
        print(f"Testing for Seed {seed + 1}")

        np.random.seed(seed)
        rd.set_seed(seed)

        #Create FNN model
        FNN_model = Sequential()

        for _ in range(layers):
            FNN_model.add(Dense(FNN_Hn, activation='relu'))

        FNN_model.add(Dense(26, activation="softmax"))

        FNN_model.compile(optimizer=optimizer,
                    loss=loss,
                    metrics=['accuracy'])

        FNN_model.build(x_train.shape)

        FNN_parameters = np.sum([np.prod(var.get_shape()) for var in FNN_model.trainable_weights])

        #Create CHN model
        CHN_model = Sequential()

        for _ in range(layers):
            CHN_model.add(CHNLayer(CHN_Hn, activation='relu'),)

        CHN_model.add(Dense(26, activation="softmax"))

        CHN_model.compile(optimizer=optimizer,
                    loss=loss,
                    metrics=['accuracy'])

        CHN_model.build(x_train.shape)

        CHN_parameters = np.sum([np.prod(var.get_shape()) for var in CHN_model.trainable_weights])
        
        # train FNN
        print("Training FNN")
        FNN_History = FNN_model.fit(x_train, y_train, epochs = epochs, batch_size = batchSize, validation_data=(x_val, y_val))

        # Evaluate FNN
        test_loss, test_accuracy = FNN_model.evaluate(x_test, y_test)
        
        # store FNN metrics
        FNN_test_accuracy.append(test_accuracy)
        FNN_test_loss.append(test_loss)
        FNN_trainloss_history.append(FNN_History.history['loss'])
        FNN_valloss_history.append(FNN_History.history['val_loss'])

        # train CHN
        print("Training CHNNet")
        CHN_History = CHN_model.fit(x_train, y_train, epochs = epochs, batch_size = batchSize, validation_data=(x_val, y_val))

        # Evaluate CHN
        test_loss, test_accuracy = CHN_model.evaluate(x_test, y_test)
        
        # store CHN metrics
        CHN_test_accuracy.append(test_accuracy)
        CHN_test_loss.append(test_loss)
        CHN_trainloss_history.append(CHN_History.history['loss'])
        CHN_valloss_history.append(CHN_History.history['val_loss'])



    # Measurements
    FNN_accuracy_mean = np.mean(FNN_test_accuracy)
    FNN_accuracy_std = np.std(FNN_test_accuracy)
    FNN_loss_mean = np.mean(FNN_test_loss)
    FNN_loss_std = np.std(FNN_test_loss)

    CHN_accuracy_mean = np.mean(CHN_test_accuracy)
    CHN_accuracy_std = np.std(CHN_test_accuracy)
    CHN_loss_mean = np.mean(CHN_test_loss)
    CHN_loss_std = np.std(CHN_test_loss)



    # store results
    with open(f"Letter/letterArch{arch+1}.txt", "w") as metFile:
        # FNN results
        metFile.write("FNN MODEL\n")
        metFile.write(f"Params: {FNN_parameters}\n")
        metFile.write("ACCURACY\n")
        metFile.write(f"Mean: {FNN_accuracy_mean}\n")
        metFile.write(f"std: {FNN_accuracy_std}\n")
        metFile.write("LOSS\n")
        metFile.write(f"Mean: {FNN_loss_mean}\n")
        metFile.write(f"std: {FNN_loss_std}\n\n")

        # CHN results
        metFile.write("CHN MODEL\n")
        metFile.write(f"Params: {CHN_parameters}\n")
        metFile.write("ACCURACY\n")
        metFile.write(f"Mean: {CHN_accuracy_mean}\n")
        metFile.write(f"std: {CHN_accuracy_std}\n")
        metFile.write("LOSS\n")
        metFile.write(f"Mean: {CHN_loss_mean}\n")
        metFile.write(f"std: {CHN_loss_std}")



    # Generate Graphs
    for seed in range(num_seeds):
        plt.plot(FNN_valloss_history[seed], color="c", linewidth=2)
        plt.plot(CHN_valloss_history[seed], color="r", linewidth=2)
        plt.plot(FNN_trainloss_history[seed], color="c", linewidth=0.5)
        plt.plot(CHN_trainloss_history[seed], color="r", linewidth=0.5)
        plt.title(f"Letter: Architecture {arch+1}")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend(["FNN"] + ["CHN"])
        plt.savefig(f"Letter/letterArch{arch+1}Seed{seed+1}.pdf")
        plt.clf()

    layers += 2