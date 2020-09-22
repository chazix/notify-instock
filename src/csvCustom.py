import codecs
import collections.abc
import os
from datetime import datetime as dt

class CCsvObject:
    def FormatCsv(self):
        raise NotImplementedError()

class CCsvOutputData:
    def __init__(self, categories, name, url, header):
        self.m_name   = name
        self.m_url    = url
        self.m_header = header
        self.m_data   = {c: [] for c in categories}

    def AddData(self, c, data):
        # grow m_data by the values in the passed in iterable
        if isinstance(data, collections.abc.Iterable):
            self.m_data[c].extend(data)
            return
        # signular addition
        self.m_data[c].append(data)

    def Count(self):
        items = 0
        for _,v in self.m_data.items():
            items += len(v)
        return items

    def OutputCsv(self, outdir, filename, spacing=0):
        outdir      += '/' if not outdir.endswith('/') else ''
        outputFile   = '{0}{1}.csv'.format(outdir, filename)
        # we need utf-8, because of potential accent characters
        with codecs.open(outputFile, 'w', 'utf-8') as f:
            f.write('{0}\n'.format(self.m_header))
            for _,values in self.m_data.items():
                for d in values:
                    f.write('{0}\n'.format(d.FormatCsv()))

        pad = ''
        for _ in range(0, spacing):
            pad += ' '
        print('{0}{1}{2}'.format(
            pad,
            'Saving File: ',
            '{0}'.format(outputFile))
        )

    def WriteCsvFile(self, outdir, extrapath='', spacing=0):
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        currentTime = dt.now()
        timeFormat  = currentTime.strftime('%m%d%Y')
        outputFileName = '{0}_{1}{2}'.format(self.m_name, timeFormat, extrapath)
        self.OutputCsv(outdir, outputFileName, spacing=spacing)