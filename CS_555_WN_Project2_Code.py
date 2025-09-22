supported_tags = {
    'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS',
    'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE',
    'HEAD', 'TRLR', 'NOTE'
}

individuals = []
families = []

curr_indiv = None
curr_fam = None
birth = False
death = False
marriage = False
divorce = False

def parse_line(line):
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''

    return level, tag, valid, arguments

with open('Gedcom-file.ged', 'r') as file:
    for line in file:
        print(f'--> {line.strip()}')
        level, tag, valid, arguments = parse_line(line)
        print(f'<-- {level}|{tag}|{valid}|{arguments}')

        if level == '0':
            if 'INDI' in line:
                if curr_indiv:
                    individuals.append(curr_indiv)
                curr_indiv = {'NAME': arguments.split()[0]}
            elif 'FAM' in line:
                if curr_fam:
                    families.append(curr_fam)
                curr_fam = {'NAME': arguments.split()[0]}
        elif level == '1':
            if tag == 'NAME' and curr_indiv is not None:
                curr_indiv['NAME'] = arguments
            elif tag == 'SEX' and curr_indiv is not None:
                curr_indiv['SEX'] = arguments
            elif tag == 'BIRT':
                birth = True
            elif tag == 'DEAT':
                death = True
            elif tag == 'MARR':
                marriage = True
            elif tag == 'DIV':
                divorce = True
            elif tag == 'HUSB' and curr_fam is not None:
                curr_fam['HUSB'] = arguments
            elif tag == 'WIFE' and curr_fam is not None:
                curr_fam['WIFE'] = arguments
            elif tag == 'CHIL' and curr_fam is not None:
                curr_fam.setdefault('CHIL', []).append(arguments)
        elif level == '2' and tag == 'DATE':
            if birth and curr_indiv is not None:
                curr_indiv['BIRT'] = arguments
                birth = False
            elif death and curr_indiv is not None:
                curr_indiv['DEAT'] = arguments
                death = False
            elif marriage and curr_fam is not None:
                curr_fam['MARR'] = arguments
                marriage = False
            elif divorce and curr_fam is not None:
                curr_fam['DIV'] = arguments
                divorce = False

    if curr_indiv:
        individuals.append(curr_indiv)
    if curr_fam:
        families.append(curr_fam)

print(f'\nNumber of Individuals: {len(individuals)}')
print(f'Number of Families: {len(families)}')


print('\nIndividuals:')
for ind in individuals:
    print(ind)

print('\nFamilies:')
for fam in families:
    print(fam)
supported_tags = {
    'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS',
    'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE',
    'HEAD', 'TRLR', 'NOTE'
}

individuals = []
families = []

curr_indiv = None
curr_fam = None
birth = False
death = False
marriage = False
divorce = False

def parse_line(line):
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''

    return level, tag, valid, arguments

with open('Gedcom-file.ged', 'r') as file:
    for line in file:
        print(f'--> {line.strip()}')
        level, tag, valid, arguments = parse_line(line)
        print(f'<-- {level}|{tag}|{valid}|{arguments}')

        if level == '0':
            if 'INDI' in line:
                if curr_indiv:
                    individuals.append(curr_indiv)
                curr_indiv = {'ID': tag.strip().replace('@', '')}
            elif 'FAM' in line:
                if curr_fam:
                    families.append(curr_fam)
                curr_fam = {'ID': tag.strip().replace('@', '')}
        elif level == '1':
            if tag == 'NAME' and curr_indiv is not None:
                curr_indiv['NAME'] = arguments
            elif tag == 'SEX' and curr_indiv is not None:
                curr_indiv['SEX'] = arguments
            elif tag == 'BIRT':
                birth = True
            elif tag == 'DEAT':
                death = True
            elif tag == 'MARR':
                marriage = True
            elif tag == 'DIV':
                divorce = True
            elif tag == 'HUSB' and curr_fam is not None:
                curr_fam['HUSB'] = arguments.strip().replace('@', '')
            elif tag == 'WIFE' and curr_fam is not None:
                curr_fam['WIFE'] = arguments.strip().replace('@', '')
            elif tag == 'CHIL' and curr_fam is not None:
                curr_fam.setdefault('CHIL', []).append(arguments.strip().replace('@', ''))
        elif level == '2' and tag == 'DATE':
            if birth and curr_indiv is not None:
                curr_indiv['BIRT'] = arguments
                birth = False
            elif death and curr_indiv is not None:
                curr_indiv['DEAT'] = arguments
                death = False
            elif marriage and curr_fam is not None:
                curr_fam['MARR'] = arguments
                marriage = False
            elif divorce and curr_fam is not None:
                curr_fam['DIV'] = arguments
                divorce = False

    if curr_indiv:
        individuals.append(curr_indiv)
    if curr_fam:
        families.append(curr_fam)
#Reorganize family data to match order and add spouse names for families:
for fam in families:
    fam_id = fam.get('ID', 'NA')
    married=fam.get('MARR', 'NA')
    divorced=fam.get('DIV', 'NA')
    husb_id=fam.get('HUSB', 'NA')
    wife_id=fam.get('WIFE', 'NA')
    children=fam.get('CHIL', [])
#find spouse names 
    husb_name = 'NA'
    wife_name = 'NA'

    if husb_id != 'NA':
        for ind in individuals:
            if ind.get('ID') == husb_id:
                husb_name = ind.get('NAME', 'NA')
                break

    if wife_id != 'NA':
        for ind in individuals:
            if ind.get('ID') == wife_id:
                wife_name = ind.get('NAME', 'NA')
                break

#reorganize family in desired order
    fam.clear()
    fam['ID'] = fam_id
    fam['Married'] = married
    fam['Divorced'] = divorced
    fam['Husband ID'] = husb_id
    fam['Husband Name'] = husb_name
    fam['Wife ID'] = wife_id
    fam['Wife Name'] = wife_name
    fam['Children'] = children

#Number of individuals and families
print(f'\nNumber of Individuals: {len(individuals)}')
print(f'Number of Families: {len(families)}')

#sort individuals by ID 

individuals.sort(key=lambda x: x.get('ID', ''))


#print individuals and families

print('\nIndividuals:')
for ind in individuals:
    print(ind)

print('\nFamilies:')
for fam in families:
    print(fam)
