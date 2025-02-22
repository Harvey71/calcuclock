import png
import sys

def convert(char):
    print('Converting ' + char)
    r = png.Reader(file=open('../imgs/' + char + '.png', 'rb'))
    (w, h, rows, info) = r.read()
    w_bytes = (w + 7) // 8
    buffer = bytearray(w_bytes * h)
    for y, row in enumerate(rows):
        for x, (r, g, b) in enumerate(zip(row[0::3], row[1::3], row[2::3])):
            if r != 255:
                buffer[y * w_bytes + x // 8] |= 1 << (7 - x % 8)
    with open('../code/' + char + '.buf', 'wb') as f:
        f.write(buffer)

chars = '0123456789hm+-xd'
for char in chars:
    convert(char)
