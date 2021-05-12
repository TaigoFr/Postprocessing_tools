
#####################################################################
# class to read the usual outputs from SmallDataIO C++ GRChombo class
#####################################################################

# The expected format is one or more rows of headers (starting with #)
# and then subsequent rows of coordinates and data

# For "Extraction" dump type of files, the data is further divided into blocks
# ("header1|data1 \n\n header2|data2 ...")
# Here assuming that a single empty line is what is dividing blocks
# (in reality files typically have 2 of dividing empty lines between blocks)

import glob # to read directories based on a regex expression

# like a C-struct
class Block:
    ### public
    def __init__(self): # constructor
        self._headers = []
        self._data = []

    def getData(self):    return self._data
    def getHeaders(self): return self._headers

    def add(self, line):
        line = line.strip() # just to make sure
        self.__add_header(line) if line.startswith('#') else self.__add_data(line)

    ### private
    def __add_header(self, line):
        line = line[1:] # remove '#'
        # split with >=2 whitespaces such that pieces as 'r = ' or 'time =' stay together
        # (there is a risk of heaving 2 very big headers, change separator to 'None' if you have that problem)
        self._headers.append( [s.strip() for s in line.split('  ') if s] )
    def __add_data(self, line):
        self._data.append( [float(s.strip()) for s in line.split() if s] )

class File:
    ### public
    def __init__(self, filename, read = True):
        self.filename = filename
        self.blocks = []
        self._was_read = False
        if read: self.read()

    def getBlock(self, idx):
        assert(self._was_read)
        assert(isinstance(idx, int) and idx>=0 and idx < len(self.blocks))
        return self.blocks[idx]
    def wasRead(self): return self._was_read
    def getName(self): return self.filename

    # methods assuming there is only 1 block
    def getData(self):    return self.getBlock(0).getData()
    def getHeaders(self): return self.getBlock(0).getHeaders()

    def read(self):
        found_new_block = True # start by adding 1st Block
        with open(self.filename) as file:
            for line in file:
                line = line.strip()
                if line: # if line is not empty
                    if found_new_block:
                        self.blocks.append(Block())
                        found_new_block = False
                    self.blocks[-1].add(line)
                else:
                    found_new_block = True
        self._was_read = True

class SmallDataIOReader:
    def __init__(self, file_prefix, read = True):
        self.files = [File(filename, read) for filename in glob.glob(file_prefix)]

    def getFile(self, idx):
        assert(isinstance(idx, int) and idx>=0 and idx < len(self.files))
        return self.files[idx]

    # methods assuming there is only 1 file, 1 block
    def getData(self):    return self.getFile(0).getData()
    def getHeaders(self): return self.getFile(0).getHeaders()

# # Usage 1:
# filename = "data/Weyl_integral_64.dat"
# reader = File(filename)
# print(reader.getHeaders())
# print(reader.getData()[0:2])
# print(len(reader.blocks))
# print(len(reader.getHeaders()))
# print(len(reader.getData()))

# # Usage 2
# file_prefix = "data/Weyl_integral_*.dat"
# reader = SmallDataIOReader(file_prefix)
# print(reader.getFile(0).getName())
# print(reader.getFile(0).wasRead())
# print(reader.getFile(0).getHeaders())
