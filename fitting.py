from scipy.optimize import curve_fit
from scipy.special import wofz
import numpy as np
import matplotlib.cm as cm


def Lorentzian(x, center, intensity, w):
    y = w ** 2 / (4 * (x - center) ** 2 + w ** 2)
    return intensity * y


def Gaussian(x, center, intensity, sigma):
    y = np.exp(-1 / 2 * (x - center) ** 2 / sigma ** 2)
    return intensity * y


def Voigt(xval, center, intensity, lw, gw):
    # lw : HWFM of Lorentzian
    # gw : sigma of Gaussian
    if gw == 0:
        gw = 1e-10
    z = (xval - center + 1j*lw) / (gw * np.sqrt(2.0))
    w = wofz(z)
    model_y = w.real / (gw * np.sqrt(2.0*np.pi))
    intensity /= model_y.max()
    return intensity * model_y


class Fit:
    def __init__(self):
        self.x = None
        self.y = None
        self.params = None
        self.num_func = 0
        self.func = Lorentzian
        self.num_params_per_func = 3

        self.y_sum = None
        self.y_list = []

        self.params_fit = None
        self.pcov = None

    def load_data(self, x, y):
        self.x = x
        self.y = y

    def set_function(self, name):
        if name == 'Lorentzian':
            self.func = Lorentzian
            self.num_params_per_func = 3
        elif name == 'Gaussian':
            self.func = Gaussian
            self.num_params_per_func = 3
        elif name == 'Voigt':
            self.func = Voigt
            self.num_params_per_func = 4

    def set_params(self, params):
        self.params = params
        self.num_func = int(len(self.params) / self.num_params_per_func)

    def superposition(self, x, *params):
        # 全てのyを足し合わせ
        self.y_sum = np.zeros_like(x)
        for i in range(self.num_func):
            p = params[i * self.num_params_per_func:(i + 1) * self.num_params_per_func]
            self.y_sum += self.func(x, *p)

        # バックグラウンドを追加
        self.y_sum = self.y_sum + params[-1]

        return self.y_sum

    def fit(self):
        if self.params is None:
            return False
        try:
            self.params_fit, self.pcov = curve_fit(self.superposition, self.x, self.y, p0=self.params)
        except RuntimeError:
            return False

        return True

    def make_y_list(self):
        if self.x is None or self.y is None or self.params_fit is None:
            return False

        self.y_list = []
        self.y_list.append(self.superposition(self.x, *self.params_fit))
        for i in range(self.num_func):
            p = self.params_fit[i * self.num_params_per_func:(i + 1) * self.num_params_per_func]
            y = self.func(self.x, *p)
            self.y_list.append(y)

        # バックグラウンドを追加
        self.y_list.append(np.ones_like(self.x) * self.params_fit[-1])
        return True

    def get_y_list(self):
        return self.y_list

    def draw(self, ax):
        ok = self.make_y_list()
        if not ok:
            return False

        for i, y in enumerate(self.y_list):
            if i == 0 or i == len(self.y_list) - 1:
                ax.plot(self.x, y, color='r')
            else:
                ax.fill_between(self.x, y, self.y_list[-1], facecolor=cm.rainbow(i / len(self.y_list)), alpha=0.6)

