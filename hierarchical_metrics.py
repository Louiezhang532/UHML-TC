from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence


def ancestor_expand(
    labels: Collection[str], parent_by_id: Mapping[str, str | None]
) -> set[str]:
    expanded: set[str] = set()

    for label in labels:
        current: str | None = label
        visited: set[str] = set()
        while current is not None:
            if current in visited:
                raise ValueError("Cycle detected in taxonomy")
            visited.add(current)
            expanded.add(current)
            current = parent_by_id.get(current)

    return expanded


def example_based_hf1(
    true_docs: Sequence[Collection[str]],
    predicted_docs: Sequence[Collection[str]],
    parent_by_id: Mapping[str, str | None],
) -> float:
    if len(true_docs) != len(predicted_docs):
        raise ValueError("Document counts differ")
    if not true_docs:
        return 0.0

    score_sum = 0.0
    for true_labels, predicted_labels in zip(true_docs, predicted_docs):
        reference = ancestor_expand(true_labels, parent_by_id)
        prediction = ancestor_expand(predicted_labels, parent_by_id)
        if not reference and not prediction:
            score_sum += 1.0
        elif reference and prediction:
            score_sum += 2.0 * len(reference & prediction) / (len(reference) + len(prediction))

    return score_sum / len(true_docs)


def micro_f1(
    true_docs: Sequence[Collection[str]], predicted_docs: Sequence[Collection[str]]
) -> float:
    if len(true_docs) != len(predicted_docs):
        raise ValueError("Document counts differ")

    true_positive = 0
    false_positive = 0
    false_negative = 0
    for true_labels, predicted_labels in zip(true_docs, predicted_docs):
        reference = set(true_labels)
        prediction = set(predicted_labels)
        true_positive += len(reference & prediction)
        false_positive += len(prediction - reference)
        false_negative += len(reference - prediction)

    denominator = 2 * true_positive + false_positive + false_negative
    return 2 * true_positive / denominator if denominator else 0.0
