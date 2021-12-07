if __name__ == '__main__':
    with open('grammar.txt', 'r') as f:
        lines = f.readlines()

    grammar = []
    import re

    for line in lines:
        key, ap = line.split('->')
        aps = ap.split('|')

        key = key.strip()
        dash = re.search(r'\w(-)\w', key)
        while dash:
            dash = dash.start() + 1
            key = key[:dash] + 'O' + key[dash + 1:]
            dash = re.search(r'\w(-)\w', key)

        for ap in aps:
            ap = ap.strip()
            dash = re.search(r'\w-\w', ap)
            while dash:
                dash = dash.start() + 1
                ap = ap[:dash] + 'O' + ap[dash + 1:]
                dash = re.search(r'\w-\w', ap)

            grammar.append(' '.join([key, ap]))

    print(grammar)

    with open('grammar.txt', 'w') as f:
        f.write('\n'.join(grammar))
