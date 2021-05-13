
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
import operator # do things like operator.iadd(a,b)
import copy # use deepcopy

# contains headers and data of a block of data of SmallDataIO files
class Block:
    ### public
    def __init__(self): # constructor
        self._headers = []
        self._data = []
        self._num_labels = None # undefined

    def getData(self):    return self._data
    def getHeaders(self): return self._headers

    def numRows(self):    return len(self._data)
    def numColumns(self): return len(self._data[0])
    def numLabels(self):  return self._num_labels
    def numValues(self):  return self.numColumns() - self.numLabels()

    def addLine(self, line):
        line = line.strip() # just to make sure
        self.__add_header_line(line) if line.startswith('#') else self.__add_data_line(line)

    # complexify columns in pairs, useful for Weyl4 (by default do from the 2nd column til the end)
    def complexifyColumns(self, col_start = -1, col_end = -1):
        if col_start < 0: col_start = self.numLabels()
        if col_end   < 0: col_end   = self.numColumns() - 1

        assert(isinstance(col_end, int) and isinstance(col_start, int))
        assert(col_end >= 0 and col_end < self.numColumns())
        assert(col_start >= 0 and col_start < self.numColumns())
        assert((col_end - col_start + 1) % 2 == 0) # we complexify every pair
        columns = self.transposeData(self._data)
        newColumns = []
        for col in range(col_start):
            newColumns.append(columns[col])
        for col in range(col_start, col_end+1, 2):
            newColumns.append([(columns[col][row] + 1j * columns[col+1][row]) for row in range(len(columns[col]))])
        for col in range(col_end+1, self.numColumns()):
            newColumns.append(columns[col])

        # transpose back to row-like list
        self._data = self.transposeData(newColumns)
        return self.getData()

    def __len__(self):               return self.numRows()  # ask for 'len(Block)'
    def __getitem__(self, idx):      return self._data[idx] # ask for row 'i' as 'block[i]'
    def __setitem__(self, idx, val): self._data[idx] = val # 'block[idx] = val'

    # allow to use operators +-*/ between blocks (does not change the 'labels')
    def __add__(self, other):      return self.__operator(operator.add,      other, assign = False)
    def __iadd__(self, other):     return self.__operator(operator.iadd,     other, assign = True)
    def __sub__(self, other):      return self.__operator(operator.sub,      other, assign = False)
    def __isub__(self, other):     return self.__operator(operator.isub,     other, assign = True)
    def __mul__(self, other):      return self.__operator(operator.mul,      other, assign = False)
    def __imul__(self, other):     return self.__operator(operator.imul,     other, assign = True)
    def __truediv__(self, other):  return self.__operator(operator.truediv,  other, assign = False)
    def __itruediv__(self, other): return self.__operator(operator.itruediv, other, assign = True)

    def transposeData(self, data):
        return [list(col) for col in zip(*data)]

    ### private
    def __add_header_line(self, line):
        line = line[1:] # remove '#'
        # split with >=2 whitespaces such that pieces as 'r = ' or 'time =' stay together
        # (there is a risk of heaving 2 very big headers, change separator to 'None' if you have that problem)
        self._headers.append( [s.strip() for s in line.split('  ') if s] )
    def __add_data_line(self, line):
        if self._num_labels == None: # count number of labels if not yet done
            self._num_labels = self.__get_num_labels_from_line(line)
        self._data.append( [float(s.strip()) for s in line.split() if s] )
    def __get_num_labels_from_line(self, line): # retrieve number of labels from a line
        all_lengths = [(len(s.strip(' -'))) for s in line.split() if s] # width of each number, remove minus signs
        lengths = list(set(all_lengths)) # count how many of each
        assert(len(lengths) == 2) # labels have only length, data another length
        return all_lengths.count(min(lengths)) # assume coordinates have the minimum length

    def __operator(self, oper, obj, assign): # generic operator
        if isinstance(obj, Block):                    return self.__operator__Block(oper, obj, assign)
        elif hasattr(obj, "__len__"):                 return self.__operator__ListOfConstants(oper, obj, assign)
        elif isinstance(obj, (int, float, complex)):  return self.__operator__Constant(oper, obj, assign)
        else:                                         raise TypeError

    def __operator__Constant(self, oper, constant, assign): # generic operator that receives a constant
        return self.__operator__ListOfConstants(oper, [constant]*self.numValues(), assign)

     # generic operator that receives a list / array
    def __operator__ListOfConstants(self, oper, listOfConstants, assign):
        assert(len(listOfConstants) == self.numValues())
        num_labels = self.numLabels()
        num_columns = self.numColumns()

        out = self if assign else copy.deepcopy(self)
        for row in out:
            for col in range(num_labels, num_columns):
                row[col] = oper(row[col], listOfConstants[col - num_labels])

        return out

     # generic operator that receives another Block
    def __operator__Block(self, oper, other_block, assign):
        num_labels = self.numLabels()
        num_columns = self.numColumns()
        assert(other_block.numLabels() == num_labels)
        assert(other_block.numColumns() == num_columns)
        assert(other_block.numRows() == self.numRows())

        out = self if assign else copy.deepcopy(self)
        for row, other_row in zip(out._data, other_block):
            for col in range(num_labels, num_columns):
                row[col] = oper(row[col], other_row[col])

        out.headers = [] # doesn't make sense to mix headers
        return out

# contains all the data of a SmallDataIO file, as a list of blocks
class File:
    ### public
    def __init__(self, filename, read = True):
        self.filename = filename
        self.blocks = []
        self._was_read = False
        if read: self.read()

    def numBlocks(self): return len(self.blocks)
    def numLabels(self):  return self.getBlock(0).numLabels() # assume same in all blocks
    def numValues(self):  return self.getBlock(0).numValues() # assume same in all blocks
    def wasRead(self):   return self._was_read
    def getName(self):   return self.filename
    def getBlock(self, idx = 0):
        assert(self._was_read)
        return self.blocks[idx]

    # methods assuming there is only 1 block
    def getData(self):    return self.getBlock(0).getData()
    def getHeaders(self): return self.getBlock(0).getHeaders()
    def numRows(self):    return self.getBlock(0).numRows()
    def numColumns(self): return self.getBlock(0).numColumns()

    def __len__(self):               return self.numBlocks()   # ask for 'len(file)'
    def __getitem__(self, idx):      return self.getBlock(idx) # ask for block 'i' as 'file[i]'
    def __setitem__(self, idx, val):
        assert(self._was_read)
        self.blocks[idx] = val

    # allow to use operators +-*/ between files (does not change the 'labels')
    def __add__(self, other):      return self.__operator(operator.add,      other, assign = False)
    def __iadd__(self, other):     return self.__operator(operator.iadd,     other, assign = True)
    def __sub__(self, other):      return self.__operator(operator.sub,      other, assign = False)
    def __isub__(self, other):     return self.__operator(operator.isub,     other, assign = True)
    def __mul__(self, other):      return self.__operator(operator.mul,      other, assign = False)
    def __imul__(self, other):     return self.__operator(operator.imul,     other, assign = True)
    def __truediv__(self, other):  return self.__operator(operator.truediv,  other, assign = False)
    def __itruediv__(self, other): return self.__operator(operator.itruediv, other, assign = True)
    
    def read(self):
        assert(not self._was_read)
        self.blocks = [] # reset
        found_new_block = True # start by adding 1st Block
        with open(self.filename) as file:
            for line in file:
                line = line.strip()
                if line: # if line is not empty
                    if found_new_block:
                        self.blocks.append(Block())
                        found_new_block = False
                    self.blocks[-1].addLine(line)
                else:
                    found_new_block = True
        self._was_read = True

    ### private
    def __operator(self, oper, obj, assign): # generic operator
        if isinstance(obj, File):                    return self.__operator__File(oper, obj, assign)
        if isinstance(obj, Block):                    return self.__operator__Block(oper, obj, assign)
        elif hasattr(obj, "__len__"):                 return self.__operator__ListOfConstants(oper, obj, assign)
        elif isinstance(obj, (int, float, complex)):  return self.__operator__Constant(oper, obj, assign)
        else:                                         raise TypeError

    def __operator__Constant(self, oper, constant, assign): # generic operator that receives a constant
        return self.__operator__ListOfConstants(oper, [constant]*self.numValues(), assign)

     # generic operator that receives a list / array
    def __operator__ListOfConstants(self, oper, listOfConstants, assign):
        out = self if assign else copy.deepcopy(self)
        for b, block in enumerate(out.blocks):
            out.blocks[b] = oper(block, listOfConstants)
        return out

     # generic operator that receives another Block
    def __operator__Block(self, oper, other_block, assign):
        out = self if assign else copy.deepcopy(self)
        for b, block in enumerate(out.blocks):
            out.blocks[b] = oper(block, other_block)
        return out

     # generic operator that receives another File
    def __operator__File(self, oper, other_file, assign):
        out = self if assign else copy.deepcopy(self)
        for b, block, other_block in zip(range(self.numBlocks()), out.blocks, other_file):
            out.blocks[b] = oper(block, other_block)
        out.filename = "MixedFile" # doesn't make sense to keep either filename
        return out

# list of Files, reads a set of SmallDataIO files based on a prefix (can be just 1 as well)
class FileSet:
    ### public
    def __init__(self, file_prefix, read = True):
        self.files = [File(filename, read = read) for filename in glob.glob(file_prefix)]

    def numFiles(self):         return len(self.files)
    def getFile(self, idx = 0): return self.files[idx]

    def __len__(self):          return self.numFiles()   # ask for 'len(reader)'
    def __getitem__(self, idx): return self.getFile(idx) # ask for file 'i' as 'reader[i]'

# # Usage File class:
# filename = "data/Weyl_integral_64.dat"
# reader = File(filename)
# print(reader.getHeaders())
# print(reader.getData()[0:2])
# print(len(reader.blocks))
# print(len(reader.getHeaders()))
# print(len(reader.getData()))

# # Usage FileSet class:
# file_prefix = "data/Weyl_integral_*.dat"
# reader = FileSet(file_prefix)
# print(reader.getFile(0).getName())
# print(reader.getFile(0).wasRead())
# print(reader.getFile(0).getHeaders())
