import hyperspy.api as hs
import os
import sys
import click
from pymatchseries import MatchSeries

""" Align other signals
python run_match.py --path "/Users/michaelxu/Dropbox (MIT)/Data sharing - Michael/20220408 PMN-PT 25c_2/1216 DPC 8.00 Mx HAADF-DF4 0001.emd" --match False --discover True --align True --align_signals "HAADF,A-C,B-D" --name "1216 DPC 8.00 Mx HAADF-DF4 0001_HAADF"
"""


def open_file(path):
    try:
        signal_cube = hs.load(path, sum_frames=False, lazy=True, load_SI_image_stack=True)
    except:
        raise FileNotFoundError('')
    return signal_cube


def grab_signal(signal_cube, signal):
    title_list = []
    try:
        for i, data in enumerate(signal_cube[:]):
            i_title = data.metadata.General.title
            if i_title == signal:
                title_list.append(i_title)
                print('Using ', i_title)
                return data
    except:
        return signal_cube
    raise ValueError(
        f"img_signal not formatted correctly or does not exist in file with {title_list} available signals"
    )


def set_mx_default_configs(calculation):
    calculation.configuration["lambda"] = 200
    calculation.configuration["useCorrelationToInitTranslation"] = 0
    calculation.configuration["numExtraStages"] = 1
    calculation.configuration["startLevel"] = 8
    calculation.configuration["precisionLevel"] = 10
    calculation.configuration["refineStartLevel"] = 9
    calculation.configuration["refineStopLevel"] = 10
    # calculation.configuration["templateSkipNums"] = [5, 6]
    # calculation.configuration["templateNumOffset"] = 3
    # calculation.configuration["dontAccumulateDeformation"] = 1
    calculation.configuration["saveNamedDeformedTemplates"] = 1
    calculation.configuration["saveNamedDeformedTemplatesExtendedWithMean"] = 1
    return calculation


def set_matchseries_path(matchseries_path):
    curpath = os.environ.get('PATH')
    if matchseries_path in curpath:
        pass
    else:
        os.environ["PATH"] += os.pathsep + matchseries_path
    # os.environ.get('PATH')


def match_series(path, img_signal, config_params=None):
    data = open_file(path)
    signal = grab_signal(signal_cube=data, signal=img_signal)

    calculation = MatchSeries(signal)

    num_frames = signal.data.shape[0]
    print(f"Using {num_frames} frames for alignment")
    print(calculation.configuration)
    calculation.configuration["numTemplates"] = num_frames
    calculation = set_mx_default_configs(calculation)

    # Setting user-supplied configuration parameters in the config_params dictionary
    if config_params is not None:
        # assert(type(config_params) == dict)
        try:
            for (param, value) in config_params.items():
                calculation.configuration[f"{param}"] = value
        except (AttributeError, TypeError):
            raise AssertionError("Input var should be dict or config_params dictionary not formatted correctly")


    set_matchseries_path(matchseries_path=
                         '/Users/michaelxu/Documents/GitHub/match-series/quocGCC/projects/electronMicroscopy')

    print(calculation.path)

    completed = calculation.run()
    print(f"match completed for file at {path} using signal {img_signal}")
    return completed


def discover_matches():
    MatchSeries.discover()


def apply_match(path: str, name: str, signal_to_correct: str, save_stack: bool=True):
    import tifffile
    import numpy as np
    loaded = MatchSeries.load(name)
    data = open_file(path)
    # for signal in signal_to_correct:
    signal = grab_signal(signal_cube=data, signal=signal_to_correct)
    deformed_images = loaded.get_deformed_images(data=signal)
    print(deformed_images)
    # deformed_images.data
    deformed_images.compute()
    deformed_images.plot()
    average = deformed_images.mean()
    average.plot()
    average.change_dtype('float32')
    # median = deformed_images.median()
    # median.plot()
    # median.change_dtype('float32')
    # average.data.dtype
    parent_dir = os.path.split(path)[0]
    if os.path.exists(parent_dir):
        filename_head = os.path.join(parent_dir,
                                 os.path.splitext(average.metadata.General.original_filename)[0] + '_' +average.metadata.General.title)
        average.save(filename_head + '_average.tif')
        # median.save(filename_head + '_median.tif')

        if save_stack:
            min_contrast = deformed_images.inav[:].data[deformed_images.inav[:].data != 0].min()
            deformed_stack = np.dstack(deformed_images.inav[:].data - min_contrast)
            deformed_stack = np.rollaxis(deformed_stack, -1)
            tifffile.imsave(filename_head + '_stack.tif', deformed_stack)

from typing import Optional
@click.command()
@click.option("--path", required=False, type=click.Path(exists=True))
@click.option("--match", required=True, default=False)
@click.option("--discover", required=True, default=False)
@click.option("--align", required=True, default=False)
@click.option("--match_signal", required=False, type=str)
@click.option("--name", required=False, type=str)
@click.option("--align_signals", required=False, type=str)
@click.pass_context
def main(ctx: click.Context, path: str, match: bool, discover:bool, align: bool, match_signal: Optional[str], name: Optional[str], align_signals):
    if match:
        match_series(path=path, img_signal=match_signal)
    elif align:
        align_signals_tuple = align_signals.split(sep=',')
        for signal in align_signals_tuple:
            apply_match(path=path, name=name, signal_to_correct=signal)
    elif discover:
        discover_matches()
    else:
        raise ValueError("Neither match nor align (or signals to match/align) are specified to be performed")


if __name__ == '__main__':
    main()
