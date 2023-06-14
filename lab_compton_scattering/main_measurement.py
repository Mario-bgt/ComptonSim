import matplotlib.pyplot as plt

from functions import *
import os
from scipy.optimize import leastsq

c = 299792458  # speed of light in m/s

def E_out_expected(theta, E_in=674.942):
    """
    :param theta: angle in degrees
    :param E_in: incident energy in keV
    :return: energy in MeV
    """
    mc2 = 510.998  # mass of the electron in keV from wikipedia
    denominator = 1 + (E_in / mc2) * (1 - np.cos(np.deg2rad(theta)))
    E_out = E_in / denominator
    return E_out


angels = [20, 34, 49, 63, 78, 92, 107, 121, 136]

E_out_expected_list = [E_out_expected(angel) for angel in angels]
print(E_out_expected_list)


files = os.listdir('data')
files = [file for file in files if file.startswith('dw_ang')]

# sort the files by the angle
files = sorted(files, key=lambda x: int(x[6:8]))
print(files)

for file in files:
    counts = read_spe_file('data/' + file)
    x = marker_to_keV(np.arange(len(counts)))


def find_out_energy(file, expected_mean, expected_range=100):
    # Load and process SPE file
    spe_file_path = 'data/' + file
    counts = read_spe_file(spe_file_path)
    x = marker_to_keV(np.arange(len(counts)))

    # reduce the data to the expected range
    upper = int(keV_to_marker(expected_mean + expected_range))
    lower = int(keV_to_marker(expected_mean - expected_range))
    counts = counts[lower:upper]
    x = x[lower:upper]

    # fit the data to a gaussian
    params = fit_gaussian(x, counts)
    p0 = [np.max(counts), np.mean(x), np.std(x)]  # Initial guess for parameters
    x_fit = np.linspace(x[0], x[-1], 1000)
    y_fit = gaussian(x_fit, *params)

    # Plot the data and the fitted curve
    plt.plot(x, counts, 'b.', label='data')
    plt.plot(x_fit, gaussian(x_fit, *p0), 'g--', label='initial guess')
    plt.plot(x_fit, y_fit, 'r-', label='fit')
    plt.title('Gaussian Fit for ' + str(file))
    plt.xlabel('Energy [keV]')
    plt.ylabel('Counts')
    plt.legend()
    plt.grid()
    plt.savefig('plots/gaussian_fit_'+str(file)+'.pdf')
    plt.show()

    mean = params[1]
    std = params[2]

    return mean, std


files = ['dw_ang20_rt900.14.Spe', 'dw_ang34_rt900.06.Spe', 'dw_ang49_rt900.14.Spe', 'dw_ang63_rt300.18_pt2.Spe',
         'dw_ang78_rt300.06_pt2.Spe', 'dw_ang92_rt300.1_pt2.Spe', 'dw_ang107_rt900.32.Spe',
         'dw_ang121_rt722.36.Spe', 'dw_ang136_rt300.82.Spe', ]


# get the mean count and std for each file
means = []
stds = []
for i, file in enumerate(files):
    mean, std = find_out_energy(file, E_out_expected_list[i])
    means.append(mean)
    stds.append(std)

# plot the mean and std
plt.errorbar(angels, means, xerr=2.62, yerr=stds, fmt='b.', label='measured', capsize=3, elinewidth=1,
             markeredgewidth=1)
plt.plot(angels, E_out_expected_list, 'g--', label='expected')
plt.title('Measured and Expected Energy vs Angle')
plt.xlabel('Angle [degrees]')
plt.ylabel('Energy [keV]')
plt.grid()
plt.legend()
plt.savefig('plots/energy_vs_angle_v2.pdf')
plt.show()
