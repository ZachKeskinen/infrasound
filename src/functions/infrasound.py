

def show_period(day_list,eq_day, eq_hour, start_min, end_min, height_1, height_2, fc_low = 5, fc_high = None, sps = 200, title = None):
    """
    Show the plot of two infrasound arrays.
    """
    res = get_day(day_list, eq_day)
    if fc_high:
        res_hourly_1 = freq_filt(res[height_1], 2, fc_high, 'low')
        res_hourly_2 = freq_filt(res[height_2], 2, fc_high, 'low')
    if fc_low:
        res_hourly_1 = freq_filt(res[height_1], 2, fc_low, 'high')
        res_hourly_2 = freq_filt(res[height_2], 2, fc_low, 'high')

    res_hourly_1 = res_hourly_1.reshape(24, -1)
    res_hourly_2  = res_hourly_2.reshape(24, -1)

    f, ax = plt.subplots(2, figsize = (10, 5))

    for hour in range(res_hourly_1.shape[0]):
        if hour == eq_hour:
            start = int(start_min*60*sps)
            end = int(end_min*60*sps)
            arr1 = res_hourly_1[hour][start:end]
            arr2 = res_hourly_2[hour][start:end]
            t = np.linspace(start_min, end_min, arr1.size)
            ax[0].plot(t, arr1)
            ax[1].plot(t, arr2)
            # ax.set_ylim(0,1)
            # ax.set_xlim(0,60)
            # for a in ax:
            #     a.get_yaxis().set_visible(False)
            ax[1].set_xlabel('Minutes')
            if not title:
                ax[0].set_title(f'{eq_day} - Array at {height_1} and {height_2} m')
            else:
                ax[0].set_title(title)
            ax[0].set_ylabel(f'{height_1} m')
            ax[1].set_ylabel(f'{height_2} m')

def correlation_eq_hour(day_list,eq_day, eq_hour, height_1, height_2, wind_len_sec, fc, sps = 200):
    res = get_day(day_list, eq_day)
    hour_samps = int(res[height_1].shape[0]/24)
    res_hourly_1 = high_pass_filter(res[height_1], 2, fc)
    res_hourly_1 = res_hourly_1.reshape(24, hour_samps)
    res_hourly_2 = high_pass_filter(res[height_2], 2, fc)
    res_hourly_2  = res_hourly_2.reshape(24, hour_samps)
    f, ax = plt.subplots(1, figsize = (10, 5))
    for hour in range(res_hourly_1.shape[0]):
        if hour == eq_hour:
            wind = wind_len_sec * sps
            arr1 = np.reshape(res_hourly_1[hour], (int(wind),int(len(res_hourly_1[hour])/wind)), 'F')
            #arr2 = arr2.reshape(-1, int(wind))
            arr2 = np.reshape(res_hourly_2[hour], (int(wind),int(len(res_hourly_2[hour])/wind)), 'F')

            # now compute Pearson
            xcorr0lag = np.sum(arr1*arr2, axis = 0)
            #xcorr0lag = sum(arr1*arr2)
            normalization = np.sqrt(np.sum(arr1**2, axis = 0)*np.sum(arr2**2, axis = 0))
            Pcoeff = xcorr0lag/normalization
            t = np.linspace(0, 60, Pcoeff.size)
            ax.plot(t, Pcoeff)
            ax.set_ylim(0,1)
            ax.set_xlim(0,60)
            ax.get_yaxis().set_visible(False)
            ax.set_xlabel('Minutes')
            ax.set_title(f'{eq_day} - Correlation between {height_1} and {height_2} m')

def correlation_plot(day_list, date, height_1, height_2, wind_len_sec, fc, sps = 200):
    res = get_day(day_list, date)
    res_hourly_1 = high_pass_filter(res[height_1], 2, fc)
    res_hourly_1 = res_hourly_1.reshape(24, -1)
    res_hourly_2 = high_pass_filter(res[height_2], 2, fc)
    res_hourly_2  = res_hourly_2.reshape(24, -1)
    f, axes = plt.subplots(24, figsize = (20, 20))
    for hour in range(res_hourly_1.shape[0]):
        wind = wind_len_sec * sps
        arr1 = np.reshape(res_hourly_1[hour], (int(wind),int(len(res_hourly_1[hour])/wind)), 'F')
        #arr2 = arr2.reshape(-1, int(wind))
        arr2 = np.reshape(res_hourly_2[hour], (int(wind),int(len(res_hourly_2[hour])/wind)), 'F')

        # now compute Pearson
        xcorr0lag = np.sum(arr1*arr2, axis = 0)
        #xcorr0lag = sum(arr1*arr2)
        normalization = np.sqrt(np.sum(arr1**2, axis = 0)*np.sum(arr2**2, axis = 0))
        Pcoeff = xcorr0lag/normalization
        ax = axes[hour]
        t = np.linspace(0, 60, Pcoeff.size)
        ax.plot(t, Pcoeff)
        ax.set_ylim(0,1)
        ax.set_xlim(0,60)
        ax.get_yaxis().set_visible(False)
        if hour == 23:
            ax.set_xlabel('Minutes')
        if hour == 0:
            ax.set_title(f'{date} - Correlation between {height_1} and {height_2} m')

def freq_filt(arr, order, fc, kind, sps = 200):
    b, a = butter(order, fc, kind, fs = sps)
    return filtfilt(b, a, arr)

def get_day(day_list, eq_day):
    day = [day for day in day_list if day == eq_day][0]
    res = {}
    ls = glob(join(in_dir, '*'+day+'*'))
    for file in ls:
                name = name_dic[basename(file).replace(day,'')[2:5]]
                if name != 'failed array':
                    tr = read(file)[0]
                    stats = tr.stats
                    sps = stats['sampling_rate']
                    assert sps == 200
                    # start = stats['starttime']
                    # end = stats['endtime']
                    channel = stats['channel']
                    name_channel = f'{name}-{channel}'
                    height = height_dic[name_channel]
                    if not np.isnan(height):
                        arr = tr.data
                        arr = arr * ac_calib
                        arr = arr - np.nanmean(arr)
                        arr_filt = freq_filt(arr, order = 2, fc = 1/10,kind = 'highpass')
                        res[height] = arr_filt
    return res

def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

def get_correlation_slices(arr, arr_ref, wind_len_sec, coeff_thresh =0.9, pa_thresh = 0.03, sps = 200):
        wind = int(wind_len_sec * sps)
        arr = np.reshape(arr, (wind, -1), 'F')
        arr_ref = np.reshape(arr_ref, (wind, -1), 'F')
        # now compute Pearson
        xcorr0lag = np.sum(arr*arr_ref, axis = 0)
        normalization = np.sqrt(np.sum(arr**2, axis = 0)*np.sum(arr_ref**2, axis = 0))
        Pcoeff = xcorr0lag/normalization
        condition = np.where(Pcoeff > coeff_thresh)[0]
        time_deltas = [timedelta(seconds = int(i*10)) for i in condition]

        arr = arr.reshape((Pcoeff.size, -1))
        arr = arr[condition]

        return arr[np.any(arr > pa_thresh, axis = 1)], time_deltas

def ave_slice_power(arr, sps = 200):
    power = arr**2
    power = 1/sps * np.sum(power, axis = 1)
    mean_power = np.sum(power)/power.size
    return mean_power

def slice_power(arr, sps = 200):
    power = arr**2
    power = 1/sps * np.sum(power, axis = 1)
    # mean_power = np.sum(power)/power.size
    return power

def plot_helioquarter(data_dict, height, date):
    hour_samps = int(data_dict[height].shape[0]/24)
    res_hourly = data_dict[height].reshape(24, hour_samps)
    f, axes = plt.subplots(24, figsize = (30, 10))
    t = np.linspace(0, 60, res_hourly.shape[1])
    for hour in range(res_hourly.shape[0]):
        ax = axes[hour]
        ax.plot(t, res_hourly[hour, :])
        ax.set_ylim(-2.5, 2.5)
        ax.get_yaxis().set_visible(False)
        if hour == 23:
            ax.set_xlabel('Minutes')
        if hour == 0:
            ax.set_title(f'{date} Helioquarter at {height} m')

def plot_helioquarter_spectrogram(data_dict, height, date, vmax = 0.000001):
    hour_samps = int(data_dict[height].shape[0]/24)
    res_hourly = data_dict[height].reshape(24, hour_samps)
    f, axes = plt.subplots(24, figsize = (20, 20))
    t = np.linspace(0, 60, res_hourly.shape[1])
    for hour in range(res_hourly.shape[0]):
        ax = axes[hour]
        f, t, Sxx = spectrogram(res_hourly[hour, :], fs = 200)
        t = t / 60
        ax.pcolormesh(t, f, Sxx, shading='gouraud', vmin = 0, vmax = vmax)
        # ax.set_ylim(-2.5, 2.5)
        ax.get_yaxis().set_visible(False)
        if hour == 23:
            ax.set_xlabel('Minutes')
        if hour == 0:
            ax.set_title(f'{date} Spectrogram at {height} m')