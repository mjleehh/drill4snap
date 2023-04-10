import base64
from io import BytesIO
from typing import Final

from PIL import Image

from .parser import ToolJob


def generate_thumbnail(drill_diameter: float):
    im = Image.new(mode="RGBA", size=(720, 480))
    buffered = BytesIO()
    im.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('ascii')


def create_file_header(spindle_power: int, drill_diameter: float):
    return f''';Header Start
;header_type: cnc
;tool_head: standardCNCToolheadForSM2
;machine: A350
;renderMethod: line
;file_total_lines: 24557
;estimated_time(s): 6908.736
;is_rotate: false
;diameter: 35
;max_x(mm): 133.31
;max_y(mm): 174.997
;max_z(mm): 80
;max_b(mm): 0
;min_x(mm): -133.313
;min_y(mm): -175
;min_b(mm): 0
;min_z(mm): -2
;work_speed(mm/minute): 300
;jog_speed(mm/minute): 1500
;power(%): 0
;work_size_x: 320
;work_size_y: 350
;origin: center
;thumbnail: data:image/png;base64,{generate_thumbnail(drill_diameter)}
;Header End

; G-code for laser engraving
; Generated by Snapmaker Luban
; G-code START <<<
G90
G21
M3 P{spindle_power}
'''


def crate_file_footer(safe_height: float):
    return f'''
; stop spindle

; go to safe height
G1 Z{safe_height} F30000
; program ends
M5
M2
'''


def drill_sequence(x: float, y: float, safe_height: float, drill_depth: float):
    return f'''G1 F300 X{x} Y{y}
G1 F100 Z-{drill_depth}
G1 F300 Z{safe_height}
'''


class GcodeWriter:
    def __init__(
            self, job: ToolJob, *,
            spindle_power: int = 100,
            safe_height: float = 25,
            drill_depth: float = 2,
    ):
        self._job: Final = job
        self._spindle_power: Final = spindle_power
        self._safe_height: Final = safe_height
        self._drill_depth: Final = drill_depth

    def write(self, out_file_name: str):
        job = self._job
        with open(f'{out_file_name}_{job.diameter}.cnc', 'w') as out_file:
            out_file.write(create_file_header(self._spindle_power, job.diameter))
            for segment in self._job.segments:
                for x, y in segment.holes:
                    out_file.write(drill_sequence(x, y, self._safe_height, self._drill_depth))

            out_file.write(crate_file_footer(self._safe_height))
