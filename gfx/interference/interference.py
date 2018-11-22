import numpy as np
import matplotlib.pyplot as plt
import scipy.misc as spio

img = spio.imread("test.png")[:,:,0]
plt.imshow(img)
plt.show()
print(img.shape)
fft = np.fft.fft2(img.astype(float))
fft = np.fft.fftshift(fft)
print(fft)

fft = np.abs(fft)
fft /= fft.max()

plt.imshow(np.log(fft))
plt.colorbar()
plt.show()

spio.imsave("out.png", np.sqrt(fft))
