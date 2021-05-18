'''
Codes below look for performance packaging and tank car codes in part 173.
'''
PERF_PACKAGING = "([\d]{1,2}[A-Z]+\d*)"
SPEC_PACKAGING_INSTRUCTIONS = "(?<=\s)(\d{2,}[A-Z]*\d*[A-Z]*)(?=[\s,].*tank)(?!\s°)"
AUTHORIZING_AGENCIES = ['AAR', 'DOT', 'IM', 'MC', 'TC']
AA_PATTERN = ["(?=[^\s])" + agency for agency in AUTHORIZING_AGENCIES]

'''
Pattern to verify an explosives packaging instruction
'''
PI_PATTERN = "\d{3}(\([a-z]\))*"

'''
SPEC_PACKAGING parses two groups, the first being the code and the 2nd being the
description.

ex:
Within "Specification 2P; inner nonrefillable metal receptacles.", it finds "2P" and
"inner nonrefillable metal receptacles"
'''
SPEC_PACKAGING = "(?<=(?<=S|s)pecification\s)([A-Z0-9]+[\s-]*[A-Z]*[0-9]+[A-Z0-9]*)(?=\sand\s)*(?=;*\s([^.]*)\.*)"

'''
SPEC_PACKAGING_2 parses the description from the above pattern to check for another code
followed by the word 'and'.
ex:
Within "Specification 3A and 3AX seamless steel cylinders.", SPEC_PACKAGING will find
groups '3A' and 'and 3AX seamless steel cylinders'. SPEC_PACKAGING_2 will parse out
 'and 3AX seamless steel cylinders' into '3AX' and 'seamless steel cylinders'.
'''
SPEC_PACKAGING_2 = "(?<=and\s)(\d[A-Z]+)(?=\s(.*))"

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