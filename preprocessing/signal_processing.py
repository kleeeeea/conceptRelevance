from lxml import etree
import re


file = '../data/scientific_corpus/Signal Processing (2002-2016).xml'


def removeNonASCII(doc, replaceWithSpace=True):
    if replaceWithSpace:
        doc = re.sub(r'[^\x00-\x7F]+', ' ', doc)
    else:
        doc = re.sub(r'[^\x00-\x7F]+', '', doc)
    # doc = ''.join(i for i in text if ord(i)<128)
    return doc


re_changeLine = re.compile(r'[\r\n]')


def removeNewLine(doc):
    return re.sub(re_changeLine, '', doc)


def fill():
    with open('../data/scientific_corpus__oneDocPerLine.txt', 'w') as f_w:
        coords = etree.iterparse(file, tag='record')
        for action, row in coords:
            title_el = row.find('title')
            abstract_el = row.find('abstract')
            content = (title_el.text + '. ') if title_el is not None else ''
            content += abstract_el.text if abstract_el is not None else ''
            l_w = removeNewLine(content)+'\n'
            try:
                f_w.write(l_w)
            except Exception, e:
                f_w.write(removeNonASCII(l_w))
                print e


def main():
    fill()


if __name__ == '__main__':
    main()
