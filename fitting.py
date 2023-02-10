from scipy.optimize import curve_fit
from scipy.special import wofz
import numpy as np
import matplotlib.cm as cm


def lorentzian(x, intensity, center, w):
    y = w ** 2 / (4 * (x - intensity) ** 2 + w ** 2)
    return center * y


def voigt(xval, *params):
    center, intensity, lw, gw = params
    # lw : HWFM of Lorentzian
    # gw : sigma of Gaussian
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
        self.func = voigt

        self.y_sum = None
        self.y_list = []

        self.params_fit = None
        self.pcov = None

    def load_data(self, x, y):
        self.x = x
        self.y = y

    def set_params(self, params):
        self.params = params
        self.num_func = int(len(self.params) / 4)

    def superposition(self, x, *params):
        # 全てのyを足し合わせ
        self.y_sum = np.zeros_like(x)
        for i in range(self.num_func):
            center = params[i * 4 + 0]
            intensity = params[i * 4 + 1]
            lw = params[i * 4 + 2]
            gw = params[i * 4 + 3]
            self.y_sum += self.func(x, center, intensity, lw, gw)

        # バックグラウンドを追加
        self.y_sum = self.y_sum + params[-1]

        return self.y_sum

    def fit(self):
        if self.params is None:
            print('パラメータをセットしてください．')
            return False
        try:
            self.params_fit, self.pcov = curve_fit(self.superposition, self.x, self.y, p0=self.params)
        except RuntimeError:
            print('パラメータを変えて実行しなおしてください．')
            return False

        print('フィッティングに成功しました．')
        return True

    def make_y_list(self):
        if self.x is None or self.y is None or self.params_fit is None:
            print('フィッティング後でなければ描画はできません．')
            return False

        self.y_list = []
        self.y_list.append(self.superposition(self.x, *self.params_fit))
        for i in range(self.num_func):
            center = self.params_fit[i * 4 + 0]
            intensity = self.params_fit[i * 4 + 1]
            lw = self.params_fit[i * 4 + 2]
            gw = self.params_fit[i * 4 + 3]
            y = self.func(self.x, center, intensity, lw, gw)
            self.y_list.append(y)

        # バックグラウンドを追加
        self.y_list.append(np.ones_like(self.x) * self.params_fit[-1])

    def get_y_list(self):
        return self.y_list

    def draw(self, ax):
        self.make_y_list()

        for i, y in enumerate(self.y_list):
            if i == 0 or i == len(self.y_list) - 1:
                ax.plot(self.x, y, color='r')
            else:
                ax.fill_between(self.x, y, self.y_list[-1], facecolor=cm.rainbow(i / len(self.y_list)), alpha=0.6)

