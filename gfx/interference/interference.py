import numpy as np
import matplotlib.pyplot as plt
import scipy.misc as spio

img = spio.imread("test.png")[:,:,0]
plt.imshow(img)
plt.show()
print(img.shape)
fft = np.fft.fft2(img.astype(float))
fft = np.fft.fftshift(fft)

fft = fft.real**2
fft /= fft.max()

plt.imshow(np.log(fft))
plt.colorbar()
plt.show()

spio.imsave("out.png", np.sqrt(fft))

#fft = np.fft.fftshift(fft)
#ifft = np.fft.ifft2(fft)
#ifft = np.fft.fftshift(ifft)
#plt.imshow(np.log(np.abs(ifft)))
#plt.show()
