; Synthetic numeric-form regression fixture, not a stock profile or hardware job.
; filament used [mm] = 0, 10, 0, 0
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
M73 P0 R1
M204 S10000
SET_VELOCITY_LIMIT ACCEL=5000 ACCEL_TO_DECEL=2500
M106 P2 S178
G1 X10 Y20 Z0.2 F1200
G17
G2 X30 Y20 I10 J0 Z1 E5
G3 X10 Y20 I-10 J0 E5
M73 P100 R0
M107 P2
M104 S0
M140 S0
M400
