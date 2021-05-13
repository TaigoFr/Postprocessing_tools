
import SmallDataIOReader, IntegrationMethod

# file_prefix = "data/Weyl4ExtractionOut_*.dat"
# reader = SmallDataIOReader(file_prefix, read = False)

# reader.getFile(0).read()
# print(reader.getFile(0).getName())
# print(reader.getFile(0).wasRead())
# print(reader.getFile(0).getHeaders())
# print(reader.getFile(0).getData()[0:2])
# print(reader.getFile(0).numBlocks())


# numFiles = reader.numFiles()
# for f in range(numFiles): # integrating in time
#     file = reader.getFile(f)
#     file.read()

#     numBlocks = file.numBlocks()
#     for b in range(numBlocks): # iterate over extraction radii
#         block = file.getBlock(b)

#         print("b = %d, f = %d" % (b , f))


# # Usage 1:
filename = "data/Weyl_integral_64.dat"
reader = SmallDataIOReader.File(filename)
print(reader.getHeaders())
print(len(reader.blocks))
print(len(reader.getHeaders()))
print(len(reader.getData()))
print(reader.numLabels())
print(reader.numValues())

reader.getBlock(0).complexifyColumns()
print(reader[0][0:2])

print(reader.numLabels())
print(reader.numValues())

# data = reader.getData()

# # data can be a list of floats, of lists, of Blocks, of Files, whatever, anything iterable!
# # def integrate(data, accumulator = None, method = IntegrationMethod.trapezium, is_periodic = False):
# #     total_steps = len(data)
# #     result = ??
# #     for step in range(total_steps):
# #         weight = dt * method.weight(step, total_steps, is_periodic)
# #         accumulator(result, data[s])
# #         # out[isurface] += m_dt * weight * in_data[istep][isurface];
    
# print(data[0][1:])

