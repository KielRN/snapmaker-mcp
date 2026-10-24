from pathlib import Path

import pytest

from snapmaker_u1_mcp import gcode

VALID = b"""; filament used [mm] = 0, 10, 0, 0
; filament used [g] = 0, 0.03, 0, 0
; filament_type = PLA;PLA;PLA;PLA
; nozzle_diameter = 0.4,0.4,0.4,0.4
; filament_diameter = 1.75,1.75,1.75,1.75
; layer_height = 0.2
G21
G90
M83
G28
T1
M104 S210
M109 S210
M140 S60
M190 S60
G1 X10 Y20 Z0.2 F1200
G1 X30 E10
M104 S0
M140 S0
M400
"""


def test_every_consumption_entry_and_executable_moves_are_inspected():
    result = gcode.inspect(VALID)
    assert result.used_tools == [1]
    assert result.filament_mm == [0, 10, 0, 0]
    assert result.filament_g == [0, 0.03, 0, 0]
    assert result.nozzle_max == [0, 210, 0, 0]
    assert result.bed_max == 60
    assert result.bounds_max == [30, 20, 0.2]


@pytest.mark.parametrize(
    "old,new,code",
    [
        (b"M104 S210", b"M104 S301", "temperature_limit"),
        (b"M140 S60", b"M140 S101", "temperature_limit"),
        (b"X30 E10", b"X271 E10", "movement_bounds"),
        (b"X30 E10", b"X-1 E10", "movement_bounds"),
        (b"G1 X30 E10", b"G91\nG1 X261 E10", "movement_bounds"),
        (b"G1 X30 E10", b"G2 X30 I10 E10", "unsupported_command"),
        (b"G1 X30 E10", b"SAVE_CONFIG", "unsupported_command"),
        (b"G1 X30 E10", b"START_PRINT", "unsupported_command"),
        (b"G1 X30 E10", b"G92 X0\nG1 X30 E10", "unsupported_parameters"),
        (b"G1 X30 E10", b"G1 XNaN E10", "invalid_gcode"),
        (b"G1 X30 E10", b"G1 X30 X40 E10", "invalid_gcode"),
        (b"G1 X30 E10", b"G1 X30 E10 M104 S999", "invalid_gcode"),
        (b"T1", b"T4", "unsupported_tool"),
        (b"0, 10, 0, 0", b"0, 0, 0, 0", "consumption_missing"),
        (b"0, 0.03, 0, 0", b"0, 0, 0, 0", "consumption_missing"),
        (b"; layer_height = 0.2", b"; layer_height = 1", "job_requirements"),
        (b"; nozzle_diameter = 0.4,0.4,0.4,0.4", b"", "job_requirements"),
        (b"G28", b"", "position_unknown"),
        (b"M109 S210", b"M109 S0", "cold_extrusion"),
        (b"M109 S210", b"M109 S210\nM104 S0", "cold_extrusion"),
        (b"G21", b"G20", "unsupported_command"),
    ],
)
def test_unsafe_or_unresolved_programs_block_preparation(old, new, code):
    with pytest.raises(gcode.ValidationError) as error:
        gcode.inspect(VALID.replace(old, new))
    assert error.value.code == code
    if new:
        assert new.decode() not in str(error.value)


def test_zero_metadata_does_not_hide_an_extruding_tool():
    with pytest.raises(gcode.ValidationError, match="consumption_missing"):
        gcode.inspect(VALID.replace(b"T1", b"T0"))


def test_executable_consumption_cannot_exceed_the_declared_requirement():
    with pytest.raises(gcode.ValidationError, match="consumption_understated"):
        gcode.inspect(VALID.replace(b"E10", b"E100"))


def test_moves_cannot_hide_unknown_coordinates_after_homing():
    with pytest.raises(gcode.ValidationError, match="position_unknown"):
        gcode.inspect(VALID.replace(b"G1 X10 Y20 Z0.2", b"G1 X10\nG1 X10 Y20 Z0.2"))


def test_g91_makes_extrusion_relative_even_after_m82():
    with pytest.raises(gcode.ValidationError, match="cold_extrusion"):
        gcode.inspect(VALID.replace(b"M400", b"M82\nG91\nT0\nG1 E1\nM400"))


def test_absolute_extrusion_requires_reset_after_tool_selection():
    with pytest.raises(gcode.ValidationError, match="position_unknown"):
        gcode.inspect(VALID.replace(b"M83", b"M82"))


def test_retraction_on_an_unused_cold_tool_also_requires_feed_and_heat():
    with pytest.raises(gcode.ValidationError, match="cold_extrusion"):
        gcode.inspect(VALID.replace(b"M400", b"T0\nG1 E-1\nM400"))


def test_total_line_limit_bounds_many_short_comments_and_commands():
    with pytest.raises(gcode.ValidationError, match="line_limit"):
        gcode.inspect(VALID + b";\n" * 500001)


def test_positive_later_mass_entry_marks_a_tool_even_without_extrusion():
    result = gcode.inspect(
        VALID.replace(b"0, 0.03, 0, 0", b"0, 0.03, 0.1, 0")
        .replace(b"0, 10, 0, 0", b"0, 10, 30, 0")
        .replace(b"M400", b"T2\nM109 S210\nM400")
    )
    assert result.used_tools == [1, 2]


def test_canonical_paths_reject_sibling_prefix_and_symlink_escape(tmp_path):
    root = tmp_path / "allowed"
    root.mkdir()
    other = tmp_path / "allowed-other"
    other.mkdir()
    secret = other / "private.gcode"
    secret.write_bytes(VALID)
    with pytest.raises(gcode.ValidationError, match="path_not_allowed"):
        gcode.read_file(str(secret), (root,), 4096)
    link = root / "link"
    try:
        link.symlink_to(other, target_is_directory=True)
    except OSError:
        # Windows junctions are available without developer-mode symlink privilege.
        import subprocess

        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(other)], check=True, capture_output=True
        )
    with pytest.raises(gcode.ValidationError, match="path_not_allowed"):
        gcode.read_file(str(link / "private.gcode"), (root,), 4096)
    local = root / "valid.gcode"
    local.write_bytes(VALID)
    path, data = gcode.read_file(str(local), (root,), 4096)
    assert path == local.resolve()
    assert data == VALID
    with pytest.raises(gcode.ValidationError, match="file_too_large"):
        gcode.read_file(str(local), (root,), 10)


@pytest.mark.parametrize("path", ["relative.gcode", "https://private.invalid/file.gcode"])
def test_file_inputs_are_absolute_host_paths_only(path):
    with pytest.raises(gcode.ValidationError):
        gcode.read_file(path, (Path.cwd(),), 4096)
