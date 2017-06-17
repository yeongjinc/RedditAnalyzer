import csv
import random
import sys

import numpy as np

from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree.tree import DecisionTreeRegressor
from sklearn import cross_validation
#from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

TOP_K = ['10']
COMMENT_NUM = ['10']
FEATURE_SET = ['contentfeatures', 'userfeatures']

''' for test
TOP_K = ['1']
COMMENT_NUM = ['10']
FEATURE_SET = ['allfeatures']
'''

CLASSIFIERS = [
    RandomForestClassifier(),
    KNeighborsClassifier(3),
#    SVC(kernel="linear", C=0.025),
#    SVC(gamma=2, C=1),
    DecisionTreeClassifier(),
#    MLPClassifier(alpha=1),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()
    ]

DIR_PATH = '/Users/yeongjin/Downloads/data/'
K_FOLD = 10

def log(l):
    print '[' + str(datetime.now()) + '] ' + l

'''
def to_float(n):
    try:
        f = float(n)
        return f
    except:
        log('Float Converting Error: ' + str(n))
        return 0.0
'''

def analyze(filePath):
    log('Analyzing ' + filePath)
    dataFile = open(filePath, "r")
    csvReader = csv.reader(dataFile, delimiter=',')
# data has no header

    p_dataset = []
    n_dataset = []
    positiveCnt = 0
    for row in csvReader:
        try:
            dummy = [float(v) for v in row]
        except:
            continue
        if row[len(row) - 1] == '1':
            p_dataset.append(row[1:]) # first column is meaningless
            positiveCnt += 1
        else:
            n_dataset.append(row[1:])

    log('Read Completed, All Data Size : ' + str(len(p_dataset) + len(n_dataset)))
    log('Positive Target Size : ' + str(positiveCnt))

    if positiveCnt > 6000:
        positiveCnt = 6000
    dataset_target = []

# 1:1 sampling to avoid class imbalance problem
    np.random.shuffle(n_dataset)
    np.random.shuffle(p_dataset)
    for row in n_dataset[:positiveCnt]:
        dataset_target.append(row)
    for row in p_dataset[:positiveCnt]:
        dataset_target.append(row)
    np.random.shuffle(dataset_target)

    dataset = []
    target = []
    for row in dataset_target:
        dataset.append([float(v) for v in row[:-1]])
        target.append(int(row[len(row) - 1]))

    log('1:1 Sampled, Dataset Size : ' + str(len(dataset)))

    for model in CLASSIFIERS:
        log('Classifier: ' + str(model))
# 10-fold cross validation
        cvScore = cross_validation.cross_val_score(model, dataset, target, cv=K_FOLD)
        #log(str(cvScore))
        log("Accuracy: %0.2f (+/- %0.2f)" % (cvScore.mean(), cvScore.std() * 2))

        f1Score = cross_validation.cross_val_score(model, dataset, target, cv=K_FOLD, scoring='f1')
        log("F1 Mean: %0.2f" % f1Score.mean())



if __name__ == "__main__":
    for top_k in TOP_K:
        for comment_num in COMMENT_NUM:
            for feature_set in FEATURE_SET:
                fileName = feature_set + '_' + top_k + '_' + comment_num + '.csv'
                analyze(DIR_PATH + fileName)
                print
                print
                print
