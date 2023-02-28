from scraper.scraper import update_jsonl_on_unique_key


def test_update_jsonl_on_unique_key(pull_requests_jsonl):
    split_point = len(pull_requests_jsonl) // 2
    originals = pull_requests_jsonl[:split_point]
    candidates = pull_requests_jsonl[split_point:]
    updated = update_jsonl_on_unique_key(originals, candidates, "pr_id")
    assert updated == pull_requests_jsonl


def test_update_jsonl_on_unique_key_with_duplicate(pull_requests_jsonl_duplicate):
    split_point = len(pull_requests_jsonl_duplicate) // 2
    originals = pull_requests_jsonl_duplicate[:split_point]
    candidates = pull_requests_jsonl_duplicate[split_point:]
    updated = update_jsonl_on_unique_key(originals, candidates, "pr_id")
    assert updated != pull_requests_jsonl_duplicate
