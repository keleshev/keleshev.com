from hi import Highlighter as Hi


def test_hi():
    assert Hi().eval('text') == 'text'
    assert Hi().eval('for') == '<b>for</b>'
    assert Hi().eval('# for\nfor') == '<i># for\n</i><b>for</b>'
    assert Hi().eval('print hai') == '<b>print </b>hai'
    assert Hi().eval('print(hai)') == '<b>print</b>(hai)'


def test_integration():
    source = '''
    # Parse matrix.
    matrix = []
    for line in sys.stdin.read().splitlines():
        row = []
        for digits in line.split(' '):
            number = int(digits)
            row.append(number)
        matrix.append(row)

    # Rows.
    matrix = list(matrix)
    '''
    print Hi().eval(source)
    assert 0

