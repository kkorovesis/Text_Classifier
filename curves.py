# -*- coding: utf-8 -*-
# !/usr/bin/python

from scipy import interp
from sklearn.svm import SVC
from sklearn.metrics import auc
from sklearn.cross_validation import KFold
from sklearn.learning_curve import learning_curve
from sklearn.metrics import precision_recall_curve
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import matplotlib.pyplot as plt
import numpy as np


def randomize(X: object, Y: object) -> object:
    permutation = np.random.permutation(Y.shape[0])
    X2 = X[permutation, :]
    Y2 = Y[permutation]
    return X2, Y2


def init_sklearn_classifier(classifier_name, cost=100, n_jobs=4):

    classifier_list = {
        "SVM Linear": SVC(kernel='linear', C=cost),
        "k-NN": KNeighborsClassifier(n_neighbors=100, n_jobs=n_jobs),
        "Random Forests": RandomForestClassifier(n_estimators=350, max_features=20, max_leaf_nodes=600, n_jobs=n_jobs),
        "Logistic Regression L1": LogisticRegression(C=cost, penalty='l1', n_jobs=n_jobs),
        "Logistic Regression L2": LogisticRegression(C=cost, penalty='l1', n_jobs=n_jobs),
        "Logistic Regression Stochastic Gradient Descent" : LogisticRegression(C=cost, penalty='l2',
                                                                    class_weight='balanced',max_iter=500, solver='sag'),
    }
    return classifier_list[classifier_name]


def plot_precision_recall(x, y, classifier_name, cost=100, n_folds=10, n_jobs=4, pos_label=0):

    mean_recall = np.linspace(0, 1, 10)
    reversed_mean_precision = 0.0

    kf = KFold(len(x), shuffle=True, n_folds=n_folds)
    for train_index, test_index in kf:
        train_set, test_set, train_labels, test_labels = x[train_index], x[test_index], y[train_index], y[test_index]
        classifier = init_sklearn_classifier(classifier_name, cost, n_jobs)
        classifier.fit(train_set, train_labels)
        predicted_labels = classifier.predict(test_set)

        precision, recall, _ = precision_recall_curve(test_labels, predicted_labels, pos_label=pos_label)

        reversed_recall = np.fliplr([recall])[0]
        reversed_precision = np.fliplr([precision])[0]

        reversed_mean_precision += interp(mean_recall, reversed_recall, reversed_precision)
        reversed_mean_precision[-1] = 0.0

    reversed_mean_precision /= n_folds
    reversed_mean_precision[0] = 1.0

    mean_auc_pr = auc(mean_recall, reversed_mean_precision)
    plt.plot(mean_recall, reversed_mean_precision, label='%s C = %s (area = %0.2f)' %
                                                         (classifier_name, cost, mean_auc_pr), lw=1)
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision Recall')
    plt.legend(loc="lower right")
    plt.show()


def plot_learning_curve(x, y, classifier_name, cost=100, n_folds=10, n_jobs=4):
    
    x2,y2 = randomize(x,y)

    clf = init_sklearn_classifier(classifier_name, cost, n_jobs)

    plt.figure()
    plt.title('Learning Curves : ' + classifier_name)
    plt.ylim(0.0, 1.01)
    plt.xlabel("Training Examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(clf, x2, y2,
                                                            cv=n_folds,
                                                            n_jobs=n_jobs,
                                                            train_sizes=np.linspace(.1, 1.0, 5))
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")
    plt.legend(loc="best")

    plt.show()