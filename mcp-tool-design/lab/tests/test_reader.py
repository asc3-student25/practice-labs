from log_tools.reader import count_by_level, list_log_files, search

LOG_DIR = "sample_logs"


def test_list_log_files_returns_app_log():
    assert "app.log" in list_log_files(LOG_DIR)


def test_search_finds_redis_entries():
    results = search(LOG_DIR, r"redis", level="ERROR")
    assert len(results) >= 2
    assert all("redis" in r["message"].lower() for r in results)
    assert all(r["level"] == "ERROR" for r in results)


def test_search_respects_limit():
    results = search(LOG_DIR, r".", limit=5)
    assert len(results) == 5


def test_count_by_level_returns_all_levels():
    counts = count_by_level(LOG_DIR)
    assert set(counts.keys()) == {"DEBUG", "INFO", "WARNING", "ERROR"}
    assert counts["ERROR"] > 0
    assert sum(counts.values()) > 20
