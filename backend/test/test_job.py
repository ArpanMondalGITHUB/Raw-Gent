# test_job.py
from services.job import get_job_status, update_job_status
from models.agent_model import ChangeType, JobStatus, RoleType
from datetime import datetime
from models.agent_model import JobStatusResponse
from services.job import job_results

def create_test_job(job_id: str):
    job_results[job_id] = JobStatusResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        messages=[],
        file_changes=[],
        created_at=datetime.now().isoformat()
    )

def test_get_job_status_returns_none_when_not_found():
    result = get_job_status("nonexistent_id")
    assert result is None


def test_get_job_status_returns_job_when_found():
    create_test_job("job_get_test")

    result = get_job_status("job_get_test")

    assert result is not None
    assert result.job_id == "job_get_test"
    assert result.status == JobStatus.QUEUED


# ── update_job_status — job not found paths ──────────────────────────────────

def test_update_job_status_returns_false_when_job_not_found():
    result = update_job_status("nonexistent_id", {"status": "running"})
    assert result is False


def test_update_job_status_creates_job_when_created_at_present():
    # if job doesn't exist BUT update has "created_at"
    # your code does: job_results[job_id] = JobStatusResponse(**update)
    new_job_data = {
        "job_id": "brand_new_job",
        "status": "queued",
        "messages": [],
        "file_changes": [],
        "created_at": datetime.now().isoformat()
    }

    result = update_job_status("brand_new_job", new_job_data)

    assert result is True
    assert get_job_status("brand_new_job") is not None


# ── update_job_status — field update paths ───────────────────────────────────

def test_update_job_status_updates_status():
    create_test_job("job_status_test")

    update_job_status("job_status_test", {"status": "running"})

    assert get_job_status("job_status_test").status == JobStatus.RUNNING


def test_update_job_status_updates_to_completed():
    create_test_job("job_completed_test")

    update_job_status("job_completed_test", {"status": "completed"})

    assert get_job_status("job_completed_test").status == JobStatus.COMPLETED


def test_update_job_status_updates_to_failed():
    create_test_job("job_failed_test")

    update_job_status("job_failed_test", {"status": "failed"})

    assert get_job_status("job_failed_test").status == JobStatus.FAILED


def test_update_job_status_updates_messages():
    create_test_job("job_messages_test")

    update_job_status("job_messages_test", {
        "messages": [
            {
                "role": "agent",
                "content": "Analyzing the code",
                "timestamp": datetime.now().isoformat()
            }
        ]
    })

    result = get_job_status("job_messages_test")
    assert len(result.messages) == 1
    assert result.messages[0].content == "Analyzing the code"
    assert result.messages[0].role == RoleType.AGENT


def test_update_job_status_updates_file_changes():
    create_test_job("job_files_test")

    update_job_status("job_files_test", {
        "file_changes": [
            {
                "file_path": "src/main.py",
                "modified_content": "print('fixed')",
                "change_type": "modified",
                "language": "python"
            }
        ]
    })

    result = get_job_status("job_files_test")
    assert len(result.file_changes) == 1
    assert result.file_changes[0].file_path == "src/main.py"
    assert result.file_changes[0].change_type == ChangeType.MODIFIED


def test_update_job_status_updates_error():
    create_test_job("job_error_test")

    update_job_status("job_error_test", {"error": "Something went wrong"})

    result = get_job_status("job_error_test")
    assert result.error == "Something went wrong"


def test_update_job_status_updates_current_step():
    create_test_job("job_step_test")

    update_job_status("job_step_test", {"current_step": "Running tests"})

    assert get_job_status("job_step_test").current_step == "Running tests"


def test_update_job_status_sets_updated_at():
    # every update should set updated_at timestamp
    create_test_job("job_timestamp_test")

    assert get_job_status("job_timestamp_test").updated_at is None
    # ↑ no updated_at before any update

    update_job_status("job_timestamp_test", {"status": "running"})

    assert get_job_status("job_timestamp_test").updated_at is not None
    # ↑ updated_at is set after update


def test_update_job_status_returns_true_on_success():
    create_test_job("job_return_test")

    result = update_job_status("job_return_test", {"status": "running"})

    assert result is True