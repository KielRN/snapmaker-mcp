"""Saved pause is independent of print labels and never a resume certificate."""

from uuid import uuid4

import httpx
import pytest
from test_uploads import prepared

from snapmaker_u1_mcp.adapter import U1Reader
from snapmaker_u1_mcp.models import RuntimeEvidence
from snapmaker_u1_mcp.runtime import normalize_runtime
from snapmaker_u1_mcp.transport import Moonraker
from snapmaker_u1_mcp.uploads import Coordinator, UploadInput


@pytest.mark.parametrize("paused", [False, True])
def test_pause_report_has_independent_exact_boolean_semantics(objects, paused):
    objects["pause_resume"] = {"is_paused": paused, "private": "PRIVATE PAUSE STATE"}
    evidence = normalize_runtime(objects)
    assert evidence.model_dump().get("pause_resume_is_paused") is paused
    assert evidence.missing_fields == []
    assert "pause_restore_state" in evidence.unestablished_dependencies
    assert "PRIVATE PAUSE STATE" not in evidence.model_dump_json()


@pytest.mark.parametrize("bad", [None, 0, 1, "false", "PRIVATE PAUSE STATE", [], {}])
def test_invalid_pause_values_stay_unknown_and_private(objects, bad):
    objects["pause_resume"] = {"is_paused": bad}
    evidence = normalize_runtime(objects)
    assert evidence.model_dump().get("pause_resume_is_paused") is None
    assert "pause_resume.is_paused" in evidence.missing_fields
    assert "PRIVATE PAUSE STATE" not in evidence.model_dump_json()


@pytest.mark.parametrize("value", [None, {}, {"other": False}])
def test_absent_pause_report_is_not_an_unpaused_default(objects, value):
    objects.pop("pause_resume", None)
    if value is not None:
        objects["pause_resume"] = value
    evidence = normalize_runtime(objects)
    assert evidence.model_dump().get("pause_resume_is_paused") is None
    assert "pause_resume.is_paused" in evidence.missing_fields


@pytest.mark.parametrize("state", ["standby", "complete", "cancelled"])
@pytest.mark.parametrize("paused", [True, False, None, 0, "false"])
async def test_idle_requires_explicit_unpaused_report(setup_upload, state, paused):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    objects["print_stats"]["state"] = state
    objects["pause_resume"] = {"is_paused": paused}
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        with Coordinator(client) as coordinator:
            response = await coordinator.reader.status()
            expected_idle = False if paused is True else (True if paused is False else None)
            assert response.data.idle is expected_idle
            assert response.data.busy is (
                True if paused is True else (False if paused is False else None)
            )
            assert response.outcome == ("ok" if type(paused) is bool else "partial")
            preparation = await prepared(coordinator, file)
            assert preparation.outcome == ("ok" if paused is False else "rejected")
            if paused is not False:
                assert preparation.errors[0].code == "printer_not_idle"
            assert printer.posts == 0


@pytest.mark.parametrize(
    "state,active", [("printing", False), ("paused", False), ("standby", True)]
)
async def test_other_busy_reports_remain_busy_with_unknown_pause(setup_upload, state, active):
    settings, printer, _ = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    objects["print_stats"]["state"] = state
    objects["virtual_sdcard"]["is_active"] = active
    objects["pause_resume"] = {}
    async with Moonraker(settings, transport=httpx.MockTransport(printer.serve)) as client:
        response = await U1Reader(client).status()
        assert response.data.busy is True
        assert response.data.idle is False


async def test_both_runtime_queries_request_only_fixed_pause_field(setup_upload):
    settings, printer, file = setup_upload
    printer.replies["/printer/objects/query"]["result"]["status"]["pause_resume"] = {
        "is_paused": False
    }
    reads = []

    async def serve(request):
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            reads.append(dict(request.url.params))
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            assert (await prepared(coordinator, file)).outcome == "ok"
    assert len(reads) == 2
    assert all(query.get("pause_resume") == "is_paused" for query in reads)


@pytest.mark.parametrize("phase", ["prepare", "preflight", "hash", "restart"])
@pytest.mark.parametrize("change", [True, None, "missing"])
async def test_saved_pause_races_block_dispatch_or_promotion(setup_upload, phase, change):
    settings, printer, file = setup_upload
    objects = printer.replies["/printer/objects/query"]["result"]["status"]
    objects["pause_resume"] = {"is_paused": False}
    reads = 0

    def mutate():
        if change == "missing":
            objects["pause_resume"].pop("is_paused", None)
        else:
            objects["pause_resume"]["is_paused"] = change

    async def serve(request):
        nonlocal reads
        if request.url.path == "/printer/objects/query" and "gcode_move" in request.url.params:
            reads += 1
            if phase == "prepare" and reads == 2:
                mutate()
        if request.url.path.startswith("/server/files/gcodes/"):
            if phase == "preflight" or (phase == "hash" and printer.posts):
                mutate()
        return await printer.serve(request)

    async with Moonraker(settings, transport=httpx.MockTransport(serve)) as client:
        with Coordinator(client) as coordinator:
            prep = await prepared(coordinator, file)
            if phase == "prepare":
                assert prep.outcome == "rejected"
                assert prep.errors[0].code == (
                    "runtime_evidence_changed" if change is True else "runtime_evidence_missing"
                )
            else:
                assert prep.outcome == "ok"
                request = UploadInput(
                    operation_id=str(uuid4()), preparation_id=prep.data.preparation_id
                )
                if phase == "restart":
                    printer.failure = "lost_without_write"
                response = await coordinator.upload(request)
                assert response.outcome == ("rejected" if phase == "preflight" else "unknown")
                if phase != "restart":
                    assert response.errors[0].code == "printer_not_idle"
                else:
                    mutate()
                    printer.files[response.data.remote_path] = file.read_bytes()
                    printer.failure = None
        if phase == "restart":
            with Coordinator(client) as coordinator:
                response = await coordinator.upload(request)
                assert response.outcome == "unknown"
                assert response.errors[0].code == "printer_not_idle"
        assert printer.posts == int(phase in {"hash", "restart"})


def test_historical_runtime_deserializes_with_unknown_saved_pause(objects):
    old = normalize_runtime(objects).model_dump()
    old.pop("pause_resume_is_paused", None)
    evidence = RuntimeEvidence.model_validate(old)
    assert "pause_resume_is_paused" in evidence.model_dump()
    assert evidence.model_dump()["pause_resume_is_paused"] is None
