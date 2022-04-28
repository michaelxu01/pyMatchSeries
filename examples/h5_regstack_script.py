
import hyperspy.api as hs
import os
import image_registration
from image_registration.fft_tools import shift
import numpy
import matplotlib.pyplot as pyplot
import h5py

file_path = "/Users/michaelxu/OneDrive - Massachusetts Institute of Technology/PMN-PT25nm_110/03022022/03-02-2022_21.58.54_DF4_HAADF.h5"
f = h5py.File(file_path, 'r')
signal = 'HAADF'
signal_key = list(f['Images'][signal].keys())
signal_stack = f['Images']['HAADF'][signal_key[0]]
print(signal_stack.shape)
signal_stack = numpy.moveaxis(signal_stack, -1, 0).astype(numpy.float64)
mean_contrast = signal_stack[signal_stack != 0].mean()

aligned_stack = numpy.full(signal_stack.shape, fill_value=mean_contrast)
aligned_stack[0,:,:] = signal_stack[0, :, :]
offx, offy = 0,0
for i in range(signal_stack.shape[0]-1):
    ref = (signal_stack[i, :, :])
    reg = (signal_stack[i+1, :, :])
    xoff, yoff = image_registration.cross_correlation_shifts(ref, reg)
    offx += xoff
    offy += yoff
    aligned_stack[i+1, :, :] = shift.shiftnd(reg.astype(numpy.float64), (-offy, -offx))
pyplot.imshow(aligned_stack[0,:,:])
# pyplot.show()

import tifffile
min_contrast = aligned_stack[aligned_stack != 0].min()
aligned_stack[aligned_stack == 0] = mean_contrast
aligned_stack_tif = numpy.dstack(aligned_stack - min_contrast)
aligned_stack_tif = numpy.rollaxis(aligned_stack_tif, -1)
aligned_stack_tif32 = aligned_stack_tif.astype('float32')
folder_path = os.path.split(file_path)[0]
tifffile.imsave(folder_path + '/reg_stack.tif', aligned_stack_tif32)

new_data = hs.signals.Signal2D(aligned_stack)

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