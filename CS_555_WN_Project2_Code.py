supported_tags = {
    'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS',
    'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE',
    'HEAD', 'TRLR', 'NOTE'
}

def parse_line(line):
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''

    return level, tag, valid, arguments

with open('CS_555_WN_Guilherme_Paim.ged', 'r') as file:
    for line in file:
        print(f'--> {line.strip()}')
        level, tag, valid, arguments = parse_line(line)
        print(f'<-- {level}|{tag}|{valid}|{arguments}')

