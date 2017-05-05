import numpy as np

from sklearn import ensemble
from sklearn.svm import OneClassSVM
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_greater_equal

from anomaly_tuning.estimators import OCSVM
from anomaly_tuning.estimators import AverageKLPE
from anomaly_tuning.estimators import MaxKLPE
from anomaly_tuning.estimators import IsolationForest


def test_score_samples_estimators():
    """Check the values of score_samples methods derived from sklearn.

    Check that the values are the same than sklearn decision_function methods.
    This only concerns OCSVM and IsolationForest.
    """

    X = np.random.randn(50, 2)

    clf1 = IsolationForest(random_state=88)
    clf1.fit(X)

    clf2 = ensemble.IsolationForest(random_state=88)
    clf2.fit(X)

    assert_array_equal(clf1.score_samples(X), clf2.decision_function(X))

    nu = 0.4
    sigma = 3.0
    gamma = gamma = 1. / (2. * sigma ** 2)
    clf1 = OCSVM(sigma=sigma, nu=nu)
    clf1.fit(X)

    clf2 = OneClassSVM(gamma=gamma, nu=nu)
    clf2.fit(X)

    assert_array_equal(clf1.score_samples(X),
                       clf2.decision_function(X).ravel())


# Toy data sets for KLPE tests
X_train = np.array([[0, 0], [1, 1], [3, 1]])
X_test = np.array([[-1, 0], [-1, 1]])


def test_averageklpe():
    """Check AverageKLPE"""
    score_train_true = - np.array([(np.sqrt(2) + np.sqrt(10)) / 2,
                                   (np.sqrt(2) + 2) / 2,
                                   (2 + np.sqrt(10)) / 2])
    pred_train_true = np.array([1, 1, 0])

    score_test_true = - np.array([(1 + np.sqrt(5)) / 2,
                                  (np.sqrt(2) + 2) / 2])
    pred_test_true = np.array([1, 1])

    # when novelty=False, i.e. scores and predict on X_train itself
    clf1 = AverageKLPE(k=2, contamination=0.4)
    clf1.fit(X_train)
    assert_equal(clf1.algo, 'average')

    score_train_attr1 = clf1.scores_fit_
    assert_array_almost_equal(score_train_attr1, score_train_true)
    score_train1 = clf1.score_samples(X_train)
    assert_array_almost_equal(score_train1, score_train_true)

    assert_greater_equal(clf1.contamination,
                         np.mean(score_train_attr1 < clf1.threshold_))

    assert_array_equal(pred_train_true, clf1.predict(X_train))

    # when novelty=True, i.e. scores and predict on X_test
    clf2 = AverageKLPE(k=2, contamination=0.4, novelty=True)
    clf2.fit(X_train)

    score_train_attr2 = clf2.scores_fit_
    assert_array_almost_equal(score_train_attr2, score_train_true)

    score_test2 = clf2.score_samples(X_test)
    assert_array_almost_equal(score_test2, score_test_true)

    assert_array_equal(pred_test_true, clf2.predict(X_test))


def test_maxklpe():
    """Check MaxKLPE"""
    score_train_true = - np.array([np.sqrt(10), 2, np.sqrt(10)])
    pred_train_true = np.array([0, 1, 0])

    score_test_true = - np.array([np.sqrt(5), 2])
    pred_test_true = np.array([1, 1])

    # when novelty=False, i.e. scores and predict on X_train itself
    clf1 = MaxKLPE(k=2, contamination=0.7)
    clf1.fit(X_train)
    assert_equal(clf1.algo, 'max')

    score_train_attr1 = clf1.scores_fit_
    assert_array_almost_equal(score_train_attr1, score_train_true)
    score_train1 = clf1.score_samples(X_train)
    assert_array_almost_equal(score_train1, score_train_true)

    assert_greater_equal(clf1.contamination,
                         np.mean(score_train_attr1 < clf1.threshold_))

    assert_array_equal(pred_train_true, clf1.predict(X_train))

    # when novelty=True, i.e. scores and predict on X_test
    clf2 = MaxKLPE(k=2, contamination=0.7, novelty=True)
    clf2.fit(X_train)

    score_train_attr2 = clf2.scores_fit_
    assert_array_almost_equal(score_train_attr2, score_train_true)

    score_test2 = clf2.score_samples(X_test)
    assert_array_almost_equal(score_test2, score_test_true)

    assert_array_equal(pred_test_true, clf2.predict(X_test))


def test_score_train_novelty_or_not():
    """Check score_fit_ attribute is the same if novelty=True of False"""

    X = np.random.randn(50, 2)

    # for AverageKLPE
    clf1 = AverageKLPE(k=10)
    clf2 = AverageKLPE(k=10, novelty=True)

    clf1.fit(X)
    clf2.fit(X)
    assert_array_equal(clf1.scores_fit_, clf2.scores_fit_)

    # for MaxKLPE
    clf3 = MaxKLPE(k=10)
    clf4 = MaxKLPE(k=10, novelty=True)

    clf3.fit(X)
    clf4.fit(X)
    assert_array_equal(clf3.scores_fit_, clf4.scores_fit_)