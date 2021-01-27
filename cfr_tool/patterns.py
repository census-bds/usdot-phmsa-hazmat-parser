PERF_PACKAGING = "([\d]{1,2}[A-Z]+\d*)"

'''
SPEC_PACKAGING parses two groups, the first being the code and the 2nd being the
description.

ex:
Within "Specification 2P; inner nonrefillable metal receptacles.", it finds "2P" and
"inner nonrefillable metal receptacles"
'''
SPEC_PACKAGING = "(?<=(?<=S|s)pecification\s)([A-Z0-9]+\s*[A-Z0-9]+)(?=;\s([\w\s]*))"

'''
TANK_CAR_CODE parses tank car codes out of the subpart headers of part 179 and
TANK_CAR_DESCRIPTION grabs its description.

ex:
Within "Subpart C—Specifications for Pressure Tank Car Tanks (Classes DOT-105, 109, 112,
114, and 120)", TANK_CAR_CODE would grab ['105', '109', '112', '114', '120'] and
TANK_CAR_DESCRIPTION would grab ['Pressure Tank Car Tanks'].
'''
TANK_CAR_CODE = "(?<=DOT.*)(\d{3}[A-Z]{0,3})(?=[\W$])"
TANK_CAR_DESCRIPTION = '(?<=Specifications\sfor\s)[\w-\s]*(?=\s\()'