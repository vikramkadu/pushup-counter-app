import os
import io
import numpy as np
import cv2
import scipy.io as sio
from math import cos, sin


def get_list_from_filenames(file_path):
    with open(file_path) as f:
        lines = f.read().splitlines()
    return lines

def normalize_landmark_point(original_point, image_size):
    '''
    original_point: (x, y)
    image_size: (W, H)
    '''
    x, y = original_point
    x -= image_size[0] // 2
    y -= image_size[1] // 2
    x /= image_size[0]
    y /= image_size[1]
    return [x, y]

def unnormalize_landmark_point(normalized_point, image_size, scale=[1,1]):
    '''
    normalized_point: (x, y)
    image_size: (W, H)
    '''
    x, y = normalized_point
    x *= image_size[0]
    y *= image_size[1]
    x += image_size[0] // 2
    y += image_size[1] // 2
    x *= scale[0]
    y *= scale[1]
    return [x, y]

def unnormalize_landmark(landmark, image_size):
    image_size = np.array(image_size)
    landmark = np.multiply(np.array(landmark), np.array(image_size)) 
    landmark = landmark + image_size / 2
    return landmark

def normalize_landmark(landmark, image_size):
    image_size = np.array(image_size)
    landmark = np.array(landmark) - image_size / 2
    landmark = np.divide(landmark, np.array(image_size))
    return landmark

def draw_landmark(img, landmark):
    im_width = img.shape[1]
    im_height = img.shape[0]
    img_size = (im_width, im_height)
    landmark = landmark.reshape((-1, 2))
    unnormalized_landmark = unnormalize_landmark(landmark, img_size)
    for i in range(unnormalized_landmark.shape[0]):
        img = cv2.circle(img, (int(unnormalized_landmark[i][0]), int(unnormalized_landmark[i][1])), 2, (0,255,0), 2)
    return img


def crop_loosely(shape, img, input_size, landmark=None):
    bbox, scale_x, scale_y = get_loosen_bbox(shape, img, input_size)
    crop_face = img[bbox[1]:bbox[3], bbox[0]:bbox[2]]
    crop_face = cv2.resize(crop_face, input_size)
    return crop_face

def get_loosen_bbox(shape, img, input_size):
    max_x = min(shape[2], img.shape[1])
    min_x = max(shape[0], 0)
    max_y = min(shape[3], img.shape[0])
    min_y = max(shape[1], 0)
    
    Lx = max_x - min_x
    Ly = max_y - min_y
    
    Lmax = int(max(Lx, Ly) * 2.0)
    
    delta = Lmax * 0.4
    
    center_x = (shape[2] + shape[0]) // 2
    center_y = (shape[3] + shape[1]) // 2
    start_x = int(center_x - delta)
    start_y = int(center_y - delta - 10)
    end_x = int(center_x + delta)
    end_y = int(center_y + delta - 10)
    
    if start_y < 0:
        start_y = 0
    if start_x < 0:
        start_x = 0
    if end_x > img.shape[1]:
        end_x = img.shape[1]
    if end_y > img.shape[0]:
        end_y = img.shape[0]

    scale_x = float(input_size[0]) / (end_x - start_x)
    scale_y = float(input_size[1]) / (end_y - start_y)
    return (start_x, start_y, end_x, end_y), scale_x, scale_y


def get_img_from_fig(fig, dpi=180):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if window_len<3:
        return x


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y


def plot_signal(x, min_val, max_val):
    
    x = np.array(x)
    width = 800
    height = 200

    if len(x) > 800:
        x = x[:-800]
    x = (x - min_val) / (max_val - min_val) * height
    img = np.zeros((height, width, 3), dtype=np.uint8)

    for i in range(1, len(x)):
        p1 = (i, int(height - x[i]))
        p2 = (i-1, int(height - x[i-1]))
        img = cv2.line(img, p1, p2, (0, 255, 0), 2)

    return img
    