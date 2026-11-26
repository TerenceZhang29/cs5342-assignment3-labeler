"""Tests for the evaluation metrics and data loading."""

import os

import pytest

import evaluate as ev
from pylabel import config
from pylabel.ingest import record_from_row

S, U, N = config.SCAM_LABEL, config.UNVERIFIED_LABEL, config.NO_LABEL
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_precision_recall_f1():
    gold = [S, S, N, N]
    pred = [S, N, S, N]
    p, r, f, support = ev.precision_recall_f1(gold, pred, S)
    assert (p, r, f, support) == (0.5, 0.5, 0.5, 2)


def test_precision_undefined_is_zero():
    assert ev.precision_recall_f1([N], [N], S)[:3] == (0.0, 0.0, 0.0)


def test_confusion_matrix_and_accuracy():
    gold, pred = [S, U, N, N], [S, N, N, U]
    matrix = ev.confusion_matrix(gold, pred)
    assert matrix[S][S] == 1 and matrix[U][N] == 1 and matrix[N][U] == 1
    assert ev.accuracy(gold, pred) == 0.5


def test_binary_collapse():
    assert ev.to_binary([S, U, N]) == ["flagged", "flagged", N]


def test_keyword_baseline_flags_warnings_too():
    assert ev.keyword_baseline("PSA: never share your seed phrase") == S
    assert ev.keyword_baseline("nice weather") == N


def test_dataset_loads_in_stream_order_and_is_well_formed():
    df = ev.load_dataset(os.path.join(ROOT, "data.csv"))
    assert len(df) >= 150
    assert set(df["expected_label"]) == {S, U, N}
    assert set(df["split"]) == {"dev", "test"}
    assert df["_t"].is_monotonic_increasing
    assert df["id"].is_unique


def test_record_from_row_parses_links_and_times():
    record = record_from_row({"id": "x", "text": "hi", "links": '["https://a.com"]',
                              "author_created_at": "2026-01-01T00:00:00Z",
                              "post_created_at": "2026-01-02T00:00:00Z"})
    assert record.links == ["https://a.com"]
    assert (record.post_created_at - record.author_created_at).days == 1
