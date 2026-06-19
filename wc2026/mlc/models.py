"""
From-scratch model zoo for the mlc lab (numpy only).

Every model exposes the same interface so the ensemble and verifier can treat
them uniformly:
    fit(X, y, scaler, **kw)      # learns from training data
    predict_proba(X) -> [n, 3]   # P(home win), P(draw), P(away win)
    predict(X) -> [n]            # argmax class

Class label convention (matches prep_data): 0 = home win, 1 = draw, 2 = away win.

Models implemented here:
    SoftmaxRegression   - multinomial logistic regression (the "full logistic")
    OrdinalLogistic     - proportional-odds ordinal logistic (W/D/L are ordered)
    DixonColesPoisson   - two Poisson goal regressions + Dixon-Coles low-score fix
    KNNClassifier       - k nearest neighbours in standardized feature space
    GaussianNaiveBayes  - Gaussian NB
    DecisionTreeClassifier (+ DecisionTreeNode) - CART with Gini, RF-aware splits
    RandomForest        - bagged trees with per-split feature subsampling
    MLPClassifier       - 1 hidden layer (ReLU) + softmax, SGD with momentum
    SoftVotingEnsemble  - average of base-model probabilities
    StackingEnsemble    - meta softmax-logistic over base-model probabilities
"""

import numpy as np

N_CLASSES = 3


# --------------------------------------------------------------------------- #
#  Multinomial logistic regression (softmax)                                  #
# --------------------------------------------------------------------------- #
class SoftmaxRegression:
    def __init__(self, cols=(0, 1, 2, 3), n_classes=N_CLASSES,
                 lr=0.5, iters=400, l2=1e-4):
        self.cols = tuple(cols)
        self.n_classes = n_classes
        self.lr = lr
        self.iters = iters
        self.l2 = l2
        self.W = None
        self.scaler = None

    def _design(self, X):
        Xc = np.asarray(X, dtype=float)[:, list(self.cols)]
        return np.hstack([np.ones((Xc.shape[0], 1)), Xc])

    @staticmethod
    def _softmax(Z):
        Z = Z - Z.max(axis=1, keepdims=True)
        E = np.exp(Z)
        return E / E.sum(axis=1, keepdims=True)

    def fit(self, X, y, scaler=None):
        self.scaler = scaler
        Xd = self._design(X)
        n, F = Xd.shape
        Y = np.zeros((n, self.n_classes))
        Y[np.arange(n), y] = 1.0
        self.W = np.zeros((self.n_classes, F))
        for _ in range(self.iters):
            P = self._softmax(Xd @ self.W.T)
            grad = (P - Y).T @ Xd / n + self.l2 * self.W
            self.W -= self.lr * grad
        return self

    def predict_proba(self, X):
        return self._softmax(self._design(X) @ self.W.T)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


# --------------------------------------------------------------------------- #
#  Proportional-odds ordinal logistic regression                             #
#  Outcomes are ordered on a "home favourability" axis: away < draw < home.   #
# --------------------------------------------------------------------------- #
class OrdinalLogistic:
    def __init__(self, cols=(0, 1, 2, 3), lr=0.3, iters=600, l2=1e-4):
        self.cols = tuple(cols)
        self.lr = lr
        self.iters = iters
        self.l2 = l2
        self.w = None
        self.theta0 = 0.0
        self.delta = 0.0   # gap = softplus(delta) keeps theta1 > theta0
        self.scaler = None

    def _feat(self, X):
        return np.asarray(X, dtype=float)[:, list(self.cols)]

    @staticmethod
    def _sig(z):
        return 1.0 / (1.0 + np.exp(-z))

    @staticmethod
    def _softplus(d):
        return np.logaddexp(0.0, d)

    def fit(self, X, y, scaler=None):
        self.scaler = scaler
        Xf = self._feat(X)
        n, F = Xf.shape
        # ordinal index: away=0, draw=1, home=2  (increasing home favourability)
        o = 2 - np.asarray(y)
        m0, m1, m2 = (o == 0), (o == 1), (o == 2)
        self.w = np.zeros(F)
        self.theta0, self.delta = 0.0, 0.0

        for _ in range(self.iters):
            gap = self._softplus(self.delta)
            eta = Xf @ self.w
            s0 = self._sig(self.theta0 - eta)
            s1 = self._sig(self.theta0 + gap - eta)
            p1 = np.clip(s1 - s0, 1e-12, None)

            cw = np.zeros(n)          # dL/deta carrier: dL/dw = (X.T @ cw)/n
            cg = np.zeros(n)          # dL/dgap carrier
            A = s1 * (1 - s1) - s0 * (1 - s0)
            cw[m0] = (1 - s0[m0])
            cw[m2] = -s1[m2]
            cw[m1] = A[m1] / p1[m1]
            cg[m2] = s1[m2]
            cg[m1] = -(s1[m1] * (1 - s1[m1])) / p1[m1]

            grad_w = Xf.T @ cw / n + self.l2 * self.w
            grad_theta0 = -cw.mean()          # theta0 acts as a sign-flipped bias
            grad_delta = cg.mean() * self._sig(self.delta)

            self.w -= self.lr * grad_w
            self.theta0 -= self.lr * grad_theta0
            self.delta -= self.lr * grad_delta
        return self

    def predict_proba(self, X):
        Xf = self._feat(X)
        gap = self._softplus(self.delta)
        eta = Xf @ self.w
        s0 = self._sig(self.theta0 - eta)
        s1 = self._sig(self.theta0 + gap - eta)
        p_away = s0
        p_draw = np.clip(s1 - s0, 0.0, None)
        p_home = 1 - s1
        P = np.vstack([p_home, p_draw, p_away]).T
        return P / P.sum(axis=1, keepdims=True)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


# --------------------------------------------------------------------------- #
#  Dixon-Coles bivariate Poisson goals model                                  #
# --------------------------------------------------------------------------- #
class DixonColesPoisson:
    def __init__(self, cols=(0, 1, 2, 3), lr=0.1, iters=500, l2=1e-4,
                 max_goals=10):
        self.cols = tuple(cols)
        self.lr = lr
        self.iters = iters
        self.l2 = l2
        self.max_goals = max_goals
        self.wh = None
        self.wa = None
        self.rho = 0.0
        self.scaler = None

    def _design(self, X):
        Xc = np.asarray(X, dtype=float)[:, list(self.cols)]
        return np.hstack([np.ones((Xc.shape[0], 1)), Xc])

    def _fit_poisson(self, Xd, yg):
        n, F = Xd.shape
        w = np.zeros(F)
        w[0] = np.log(max(yg.mean(), 1e-3))
        reg = np.ones(F) * self.l2
        reg[0] = 0.0  # don't regularize the intercept
        for _ in range(self.iters):
            lam = np.exp(np.clip(Xd @ w, -6.0, 3.5))
            grad = Xd.T @ (lam - yg) / n + reg * w
            w -= self.lr * grad
        return w

    @staticmethod
    def _pois_pmf(kmax, lam):
        # returns array [n, kmax+1] of Poisson pmf for k = 0..kmax
        ks = np.arange(kmax + 1)
        logpmf = (-lam[:, None] + ks[None, :] * np.log(lam[:, None])
                  - np.array([np.sum(np.log(np.arange(1, k + 1))) for k in ks])[None, :])
        return np.exp(logpmf)

    def _rates(self, X):
        Xd = self._design(X)
        lh = np.exp(np.clip(Xd @ self.wh, -6.0, 3.5))
        la = np.exp(np.clip(Xd @ self.wa, -6.0, 3.5))
        return lh, la

    def fit(self, X, g_home, g_away, scaler=None):
        self.scaler = scaler
        Xd = self._design(X)
        self.wh = self._fit_poisson(Xd, np.asarray(g_home, dtype=float))
        self.wa = self._fit_poisson(Xd, np.asarray(g_away, dtype=float))
        # fit rho on the four low-score cells by 1-D grid search
        lh, la = self._rates(X)
        gh, ga = np.asarray(g_home, int), np.asarray(g_away, int)
        low = (gh <= 1) & (ga <= 1)
        best_rho, best_ll = 0.0, -np.inf
        for rho in np.linspace(-0.25, 0.25, 101):
            tau = self._tau(gh[low], ga[low], lh[low], la[low], rho)
            if np.any(tau <= 0):
                continue
            ll = np.sum(np.log(tau))
            if ll > best_ll:
                best_ll, best_rho = ll, rho
        self.rho = best_rho
        return self

    @staticmethod
    def _tau(gh, ga, lh, la, rho):
        t = np.ones_like(lh, dtype=float)
        t = np.where((gh == 0) & (ga == 0), 1 - lh * la * rho, t)
        t = np.where((gh == 0) & (ga == 1), 1 + lh * rho, t)
        t = np.where((gh == 1) & (ga == 0), 1 + la * rho, t)
        t = np.where((gh == 1) & (ga == 1), 1 - rho, t)
        return t

    def predict_proba(self, X):
        lh, la = self._rates(X)
        G = self.max_goals
        ph = self._pois_pmf(G, lh)          # [n, G+1]
        pa = self._pois_pmf(G, la)          # [n, G+1]
        joint = ph[:, :, None] * pa[:, None, :]   # [n, G+1, G+1]  (home i, away j)
        r = self.rho
        joint[:, 0, 0] *= (1 - lh * la * r)
        joint[:, 0, 1] *= (1 + lh * r)
        joint[:, 1, 0] *= (1 + la * r)
        joint[:, 1, 1] *= (1 - r)
        joint = np.clip(joint, 0.0, None)
        idx = np.arange(G + 1)
        home_mask = idx[:, None] > idx[None, :]
        draw_mask = idx[:, None] == idx[None, :]
        away_mask = idx[:, None] < idx[None, :]
        H = (joint * home_mask).sum(axis=(1, 2))
        D = (joint * draw_mask).sum(axis=(1, 2))
        A = (joint * away_mask).sum(axis=(1, 2))
        P = np.vstack([H, D, A]).T
        return P / P.sum(axis=1, keepdims=True)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def most_likely_score(self, X):
        lh, la = self._rates(X)
        G = self.max_goals
        ph = self._pois_pmf(G, lh)
        pa = self._pois_pmf(G, la)
        joint = ph[:, :, None] * pa[:, None, :]
        r = self.rho
        joint[:, 0, 0] *= (1 - lh * la * r)
        joint[:, 0, 1] *= (1 + lh * r)
        joint[:, 1, 0] *= (1 + la * r)
        joint[:, 1, 1] *= (1 - r)
        flat = joint.reshape(joint.shape[0], -1).argmax(axis=1)
        return np.array([(i // (G + 1), i % (G + 1)) for i in flat])


# --------------------------------------------------------------------------- #
#  k-Nearest Neighbours                                                        #
# --------------------------------------------------------------------------- #
class KNNClassifier:
    def __init__(self, k=25):
        self.k = k
        self.X_train = None
        self.y_train = None
        self.scaler = None

    def fit(self, X, y, scaler=None):
        self.X_train = np.asarray(X, dtype=float)
        self.y_train = np.asarray(y, dtype=int)
        self.scaler = scaler
        return self

    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        out = np.zeros((X.shape[0], N_CLASSES))
        for i, x in enumerate(X):
            d = np.sum((self.X_train - x) ** 2, axis=1)
            nn = np.argpartition(d, self.k)[:self.k]
            out[i] = np.bincount(self.y_train[nn], minlength=N_CLASSES) / self.k
        return out

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


# --------------------------------------------------------------------------- #
#  Gaussian Naive Bayes                                                        #
# --------------------------------------------------------------------------- #
class GaussianNaiveBayes:
    def __init__(self, eps=1e-9):
        self.eps = eps
        self.classes = None
        self.priors = {}
        self.means = {}
        self.vars = {}
        self.scaler = None

    def fit(self, X, y, scaler=None):
        self.scaler = scaler
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        n = X.shape[0]
        self.classes = np.unique(y)
        for c in self.classes:
            Xc = X[y == c]
            self.priors[c] = Xc.shape[0] / n
            self.means[c] = Xc.mean(axis=0)
            self.vars[c] = Xc.var(axis=0) + self.eps
        return self

    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        out = np.zeros((X.shape[0], N_CLASSES))
        for i, x in enumerate(X):
            logp = np.full(N_CLASSES, -np.inf)
            for c in self.classes:
                ll = -0.5 * np.sum(np.log(2 * np.pi * self.vars[c])
                                   + (x - self.means[c]) ** 2 / self.vars[c])
                logp[c] = np.log(self.priors[c]) + ll
            logp -= logp.max()
            e = np.exp(logp)
            out[i] = e / e.sum()
        return out

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


# --------------------------------------------------------------------------- #
#  Decision tree (CART, Gini) + Random Forest                                 #
# --------------------------------------------------------------------------- #
class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None,
                 probs=None, is_leaf=False):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.probs = probs
        self.is_leaf = is_leaf


class DecisionTreeClassifier:
    def __init__(self, max_depth=6, min_samples_split=20, max_features=None,
                 n_thresholds=40, rng=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features          # None = all features
        self.n_thresholds = n_thresholds
        self.rng = rng or np.random.default_rng(0)
        self.root = None
        self.scaler = None

    @staticmethod
    def _gini(y):
        n = len(y)
        if n == 0:
            return 0.0
        p = np.bincount(y, minlength=N_CLASSES) / n
        return 1.0 - np.sum(p ** 2)

    def _best_split(self, X, y):
        n, F = X.shape
        if n < self.min_samples_split:
            return None, None
        if self.max_features and self.max_features < F:
            feats = self.rng.choice(F, self.max_features, replace=False)
        else:
            feats = range(F)
        cur = self._gini(y)
        best_g, best_f, best_t = cur, None, None
        for f in feats:
            vals = X[:, f]
            uniq = np.unique(vals)
            if len(uniq) > self.n_thresholds:
                ths = np.percentile(vals, np.linspace(2, 98, self.n_thresholds))
            else:
                ths = uniq
            for t in ths:
                lm = vals <= t
                nl = lm.sum()
                nr = n - nl
                if nl == 0 or nr == 0:
                    continue
                g = (nl * self._gini(y[lm]) + nr * self._gini(y[~lm])) / n
                if g < best_g:
                    best_g, best_f, best_t = g, f, t
        return best_f, best_t

    def _build(self, X, y, depth):
        n = X.shape[0]
        probs = np.bincount(y, minlength=N_CLASSES) / (n if n else 1)
        if len(np.unique(y)) == 1 or depth >= self.max_depth or n < self.min_samples_split:
            return DecisionTreeNode(probs=probs, is_leaf=True)
        f, t = self._best_split(X, y)
        if f is None:
            return DecisionTreeNode(probs=probs, is_leaf=True)
        lm = X[:, f] <= t
        return DecisionTreeNode(
            feature=f, threshold=t,
            left=self._build(X[lm], y[lm], depth + 1),
            right=self._build(X[~lm], y[~lm], depth + 1))

    def fit(self, X, y, scaler=None):
        self.scaler = scaler
        self.root = self._build(np.asarray(X, float), np.asarray(y, int), 0)
        return self

    def _one(self, node, x):
        while not node.is_leaf:
            node = node.left if x[node.feature] <= node.threshold else node.right
        return node.probs

    def predict_proba(self, X):
        return np.array([self._one(self.root, x) for x in np.asarray(X, float)])

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


class RandomForest:
    def __init__(self, n_trees=25, max_depth=8, min_samples_split=40,
                 max_features=2, sample_size=None, seed=42):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.sample_size = sample_size
        self.seed = seed
        self.trees = []
        self.scaler = None

    def fit(self, X, y, scaler=None):
        self.scaler = scaler
        X = np.asarray(X, float)
        y = np.asarray(y, int)
        n = X.shape[0]
        m = self.sample_size or n
        rng = np.random.default_rng(self.seed)
        self.trees = []
        for b in range(self.n_trees):
            idx = rng.integers(0, n, size=m)        # bootstrap sample
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                max_features=self.max_features,
                rng=np.random.default_rng(self.seed + b + 1))
            tree.fit(X[idx], y[idx])
            self.trees.append(tree)
        return self

    def predict_proba(self, X):
        return np.mean([t.predict_proba(X) for t in self.trees], axis=0)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


# --------------------------------------------------------------------------- #
#  Multi-layer perceptron (1 hidden layer)                                    #
# --------------------------------------------------------------------------- #
class MLPClassifier:
    def __init__(self, input_dim=4, hidden_dim=8, output_dim=N_CLASSES,
                 l2=1e-4, epochs=800, lr=0.12, momentum=0.9, seed=42):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.l2 = l2
        self.epochs = epochs
        self.lr = lr
        self.momentum = momentum
        rng = np.random.default_rng(seed)
        self.W1 = rng.standard_normal((input_dim, hidden_dim)) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = rng.standard_normal((hidden_dim, output_dim)) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros((1, output_dim))
        self.scaler = None

    @staticmethod
    def _softmax(Z):
        E = np.exp(Z - Z.max(axis=1, keepdims=True))
        return E / E.sum(axis=1, keepdims=True)

    def _forward(self, X):
        Z1 = X @ self.W1 + self.b1
        A1 = np.maximum(0, Z1)
        A2 = self._softmax(A1 @ self.W2 + self.b2)
        return Z1, A1, A2

    def fit(self, X, y, scaler=None, verbose=False):
        self.scaler = scaler
        X = np.asarray(X, float)
        y = np.asarray(y, int)
        n = X.shape[0]
        Y = np.zeros((n, self.output_dim))
        Y[np.arange(n), y] = 1.0
        vW1 = vb1 = vW2 = vb2 = 0
        for ep in range(1, self.epochs + 1):
            Z1, A1, A2 = self._forward(X)
            dZ2 = A2 - Y
            dW2 = A1.T @ dZ2 / n + self.l2 * self.W2
            db2 = dZ2.mean(axis=0, keepdims=True)
            dZ1 = (dZ2 @ self.W2.T) * (Z1 > 0)
            dW1 = X.T @ dZ1 / n + self.l2 * self.W1
            db1 = dZ1.mean(axis=0, keepdims=True)
            vW1 = self.momentum * vW1 + self.lr * dW1
            vb1 = self.momentum * vb1 + self.lr * db1
            vW2 = self.momentum * vW2 + self.lr * dW2
            vb2 = self.momentum * vb2 + self.lr * db2
            self.W1 -= vW1; self.b1 -= vb1; self.W2 -= vW2; self.b2 -= vb2
            if verbose and (ep % 200 == 0 or ep == 1):
                loss = -np.sum(Y * np.log(np.clip(A2, 1e-15, 1))) / n
                print(f"  epoch {ep:4d}/{self.epochs}  loss {loss:.4f}")
        return self

    def predict_proba(self, X):
        return self._forward(np.asarray(X, float))[2]

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


# --------------------------------------------------------------------------- #
#  Ensembles                                                                   #
# --------------------------------------------------------------------------- #
class SoftVotingEnsemble:
    """Average the probabilities of the base models (optionally weighted)."""
    def __init__(self, bases, weights=None):
        self.bases = bases                      # list of (name, fitted model)
        self.weights = weights
        self.scaler = None

    def predict_proba(self, X):
        probs = np.array([m.predict_proba(X) for _, m in self.bases])
        if self.weights is not None:
            w = np.asarray(self.weights).reshape(-1, 1, 1)
            return (probs * w).sum(axis=0) / np.sum(self.weights)
        return probs.mean(axis=0)

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


class StackingEnsemble:
    """Meta softmax-logistic trained on the base models' predicted probabilities."""
    def __init__(self, bases, meta):
        self.bases = bases                      # list of (name, fitted model)
        self.meta = meta                        # fitted SoftmaxRegression on stacked feats
        self.scaler = None

    def stack(self, X):
        return np.hstack([m.predict_proba(X) for _, m in self.bases])

    def predict_proba(self, X):
        return self.meta.predict_proba(self.stack(X))

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)
