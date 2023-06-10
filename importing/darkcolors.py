
import math, numpy, bpy, time, os
from .. import common as c





if __name__ == '__main__':
    test_matrix = {
        #    Input          customAmbient    ShadowColor Shadow  Density setting Koikatsu light Koikatsu Dark
        1:  [[1, 1, 1],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  74,  [1, 1, 1],  [.772, .851, .937]], #items
        2:  [[.5, .5, .5],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  74,  [.5, .5, .5],  [.38, .423, .466]],
        5:  [[1, 1, 1],  [.666, .666, .666, 1],  [1, 1, 1, 1],  74,  [1, 1, 1],  [.93, .93, .93]],
        6:  [[.5, .5, .5],  [.666, .666, .666, 1],  [1, 1, 1, 1],  74,  [.5, .5, .5],  [.46, .46, .46]],
        7:  [[1, 230/255, 223/255], [.666, .666, .666, 1], [0,0,0,0], 0, [1], [238/255, 196/255, 183/255]], #skin default
        8:  [[209/255, 188/255, 173/255], [.666, .666, .666, 1], [0,0,0,0], 0, [1], [195/255, 158/255, 134/255]], #skin tan
        9:  [[1, 1, 1], [.666, .666, .666, 1], [0.8304498,0.8662278,0.9411765,1], 0, [1], [209/255, 214/255, 249/255]], #hair white
        10:  [[136/255, 159/255, 114/255], [.666, .666, .666, 1], [0.6943483,0.7576795,0.8235294,1], 0, [1], [99/255, 126/255, 104/255]] #hair green
        }
    
    test = 9
    print('Test ' + str(test))
    color = test_matrix[test][0]
    shadow_color = test_matrix[test][2]
    expected_color = test_matrix[test][5]
    actual_color = hair_dark_color(color, shadow_color)
    print(expected_color)
    print(str(actual_color) + '\n')
    print('{}, {}, {}'.format(expected_color[0] - actual_color[0], expected_color[1] - actual_color[1], expected_color[2] - actual_color[2]))

