"""Evaluation metrics shared across the mlc lab.

Class order everywhere: 0 = home win, 1 = draw, 2 = away win.
"""

import numpy as np

CLASS_NAMES = {0: "Home win", 1: "Draw", 2: "Away win"}


def accuracy(P, y):
    """Top-1 accuracy, counting draws as a class you must get right."""
    return float(np.mean(np.argmax(P, axis=1) == y))


def log_loss(P, y, eps=1e-15):
    P = np.clip(P, eps, 1.0)
    return float(-np.mean(np.log(P[np.arange(len(y)), y])))


def brier(P, y):
    Y = np.zeros_like(P)
    Y[np.arange(len(y)), y] = 1.0
    return float(np.mean(np.sum((P - Y) ** 2, axis=1)))


def decisive_hit_rate(P, y):
    """Apples-to-apples with index.html's 'Model accuracy' back-test:
    draws (predicted OR actual) are excluded as pushes; hit rate = ok / (ok + miss).
    Returns (rate, ok, miss, push)."""
    pred = np.argmax(P, axis=1)
    ok = miss = push = 0
    for pk, yt in zip(pred, y):
        if pk == 1 or yt == 1:        # 1 == draw
            push += 1
        elif pk == yt:
            ok += 1
        else:
            miss += 1
    rate = ok / (ok + miss) if (ok + miss) else 0.0
    return rate, ok, miss, push


def summary(P, y):
    rate, ok, miss, push = decisive_hit_rate(P, y)
    return {
        "accuracy": accuracy(P, y),
        "log_loss": log_loss(P, y),
        "brier": brier(P, y),
        "decisive_hit_rate": rate,
        "decisive_ok": ok,
        "decisive_miss": miss,
        "decisive_push": push,
    }
