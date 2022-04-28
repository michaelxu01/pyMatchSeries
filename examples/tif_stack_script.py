
import hyperspy.api as hs
import os

import numpy

file_path = "/Users/michaelxu/OneDrive - Massachusetts Institute of Technology/PMN-PT25nm_110/03022022/03-02-2022_21.58.54_DF4_HAADF_RevSTEM/03-02-2022_21.58.54_DF4_HAADF_stack.tif"

data = hs.load(file_path)


import matplotlib.pyplot as pyplot
import numpy
if (2048-data.data.shape[1]) % 2 == 1:
    left = int(numpy.floor((2048-data.data.shape[1])/2))
    right = left + 1
else:
    left = int((2048-data.data.shape[1])/2)
    right = left
if (2048-data.data.shape[2]) % 2 == 1:
    top = int(numpy.floor((2048-data.data.shape[2])/2))
    bottom = top + 1
else:
    top = int((2048-data.data.shape[2])/2)
    bottom = top
padded = numpy.zeros(shape=(20, 2048, 2048))
mean = data.data.mean()
for i in range(data.data.shape[0]):
    padded[i,:,:] = numpy.pad(data.data[i, :, :], ((left, right), (top, bottom)), mode='constant', constant_values=0)

new_data = hs.signals.Signal2D(padded)

pyplot.imshow(new_data.data[0,:,:]-new_data.data[1,:,:])

from pymatchseries import MatchSeries

calculation = MatchSeries(new_data)

calculation.configuration

# calculation.configuration["numTemplates"]=19
calculation.configuration["lambda"]=200
calculation.configuration["numTemplates"]=20
calculation.configuration["useCorrelationToInitTranslation"]=0
calculation.configuration["numExtraStages"]=1
calculation.configuration["startLevel"]=8
calculation.configuration["precisionLevel"]=11
calculation.configuration["refineStartLevel"]=10
calculation.configuration["refineStopLevel"]=11
# calculation.configuration["templateNumOffset"] = 3
# calculation.configuration["templateSkipNums"] = []

calculation.path

os.environ.get('PATH')
path = '/Users/michaelxu/Documents/GitHub/match-series/quocGCC/projects/electronMicroscopy'
os.environ["PATH"] += os.pathsep + path
os.environ.get('PATH')

calculation.run()