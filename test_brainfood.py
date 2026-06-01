#!/usr/bin/env python3
"""
Robust test suite for BrainFood v0.1
"""
import tempfile
import shutil
from brainfood.agent import BrainFoodAgent


def setup_agent():
    tmpdir = tempfile.mkdtemp()
    return BrainFoodAgent(data_dir=tmpdir), tmpdir

def cleanup(tmpdir):
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_basic_dict_ingest():
    brain, tmp = setup_agent()
    success = brain.ingest({
        "name": "retry_with_backoff",
        "category": "development",
        "full_code": "def retry_with_backoff(): pass",
        "description": "Handles retries"
    })
    assert success is True
    comp = brain.get_atomic("development", "retry_with_backoff")
    assert comp is not None
    cleanup(tmp)
    print("\u2713 test_basic_dict_ingest passed")


def test_string_ingestion():
    """Test that raw strings are properly routed through Curator."""
    brain, tmp = setup_agent()
    success = brain.ingest("This is a clean piece of documentation or code.", category="docs")
    assert success is True
    results = brain.get_context("documentation")
    assert len(results) > 0
    cleanup(tmp)
    print("\u2713 test_string_ingestion passed")


def test_quality_gate_rejection():
    brain, tmp = setup_agent()
    success = brain.ingest("This contains a TODO: fix later", category="development")
    assert success is False
    cleanup(tmp)
    print("\u2713 test_quality_gate_rejection passed")


def test_dynamic_categories():
    brain, tmp = setup_agent()
    brain.ingest({"name": "test_comp", "category": "weird_category"}, category="misc")
    cats = brain.registry.list_categories()
    assert "weird_category" in cats
    cleanup(tmp)
    print("\u2713 test_dynamic_categories passed")


def test_enable_wipedown_toggle():
    brain_on = BrainFoodAgent(enable_wipedown=True)
    brain_off = BrainFoodAgent(enable_wipedown=False)
    assert brain_on.curator.enable_wipedown is True
    assert brain_off.curator.enable_wipedown is False
    print("\u2713 test_enable_wipedown_toggle passed")


def test_flagged_category_routing():
    brain, tmp = setup_agent()
    # Manually test the category override logic
    comp = brain.curator.curate_text("Clean content for testing", category="dev")
    if comp:
        comp["category"] = "flagged_for_review"
        brain.registry.save(comp)
    flagged = brain.get_context("flagged_for_review")
    assert any(c.get("category") == "flagged_for_review" for c in flagged)
    cleanup(tmp)
    print("\u2713 test_flagged_category_routing passed")


if __name__ == "__main__":
    print("\n=== BrainFood v0.1 Test Suite ===\n")
    test_basic_dict_ingest()
    test_string_ingestion()
    test_quality_gate_rejection()
    test_dynamic_categories()
    test_enable_wipedown_toggle()
    test_flagged_category_routing()
    print("\n=== All tests completed ===\n")
