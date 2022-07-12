
import SmallDataIOReader, IntegrationMethod, DataIntegration
import math

# import numpy as np
# import matplotlib.pyplot as plt

# weyl_prefix = "data/Weyl4ExtractionOut_*.dat"
# weyl_prefix = "data/Weyl4ExtractionOut_00039*.dat"
# reader = SmallDataIOReader.FileSet(weyl_prefix, read = False)

# # General info about files
# file0 = reader.getFile(0)
# file0.read()
# print(file0.getName())
# print(file0.wasRead())
# print(file0.getHeaders())
# print(file0.numBlocks())
# print(file0.numLabels())
# print(file0.numValues())
# print(file0.numRows())
# print(file0.numColumns())
# print(file0.getData())

method = IntegrationMethod.midpoint

# filename = "data/Weyl_integral_22.dat"
# mode22 = SmallDataIOReader.File(filename)

file_prefix = "run_g2_v3_h128/weyl4/Weyl4ExtractionOut_*.dat"
reader = SmallDataIOReader.FileSet(file_prefix, read = False)

weyl4_time_integrated = DataIntegration.integrate_in_time(reader, method, verbose = True, max_steps = -1)

# weyl4_time_integrated.complexifyColumns()

weyl4_time_integrated.addColumn(lambda row, map: row[map['Weyl4_Re'][1]] ** 2 + row[map['Weyl4_Im'][1]] ** 2)
weyl4_time_integrated.removeColumn(2, 3)

weyl4_time_and_space_integrated = DataIntegration.integrate_in_space_2d(weyl4_time_integrated,
                                        [IntegrationMethod.simpson, IntegrationMethod.trapezium],
                                        [False, True],
                                        'r',
                                        DataIntegration.spherical_area_element)

for result in weyl4_time_and_space_integrated:
    result[1][0] /= (16. * math.pi)

print(weyl4_time_and_space_integrated)

miren = [4.7611451526e-05, 8.2204283333e-06, 1.9684132443e-06, 8.2184334500e-07, 5.9685599805e-07, 5.4215204085e-07] # last step
# miren = [1.6229590143e-10, 3.4600202751e-11, 9.7476719184e-12, 3.3050439456e-12, 1.2818785018e-12, 5.5108495437e-13] # step=1
# miren = [1.6236662859e-08, 3.4605414160e-09, 9.7494833590e-10, 3.3055019484e-10, 1.2817967715e-10, 5.5105234979e-11] # step=10
for i, result in enumerate(weyl4_time_and_space_integrated):
    print(result[1][0] / miren[i])




# accumulated = integrate_in_time(mode22[0], method, accumulate = True)
# print(accumulated)
# print(integrate_in_time(mode22[0], method))
# print([0][:2])
