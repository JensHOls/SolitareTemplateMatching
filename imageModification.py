import cv2
import numpy as np

# adds padding around given image. Code in method is from: https://stackoverflow.com/questions/43391205/add-padding-to-images-to-get-them-into-the-same-shape
def addPadding(image, dimensions):
    old_image_height, old_image_width, channels = image.shape
    # create new image of desired size and color (blue) for padding
    new_image_width = dimensions[0]
    new_image_height = dimensions[1]
    color = (255, 255, 255)
    result = np.full((new_image_height, new_image_width, channels), color, dtype=np.uint8)

    # compute center offset
    x_center = (new_image_width - old_image_width) // 2
    y_center = (new_image_height - old_image_height) // 2

    # copy img image into center of result image
    result[y_center:y_center + old_image_height,
    x_center:x_center + old_image_width] = image
    # showImage("output", result)
    return result


# Code in method is from: https://pyimagesearch.com/2021/01/20/opencv-rotate-image/
def rotate(image, rotation):
    # grab the dimensions of the image and calculate the center of the
    # image
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # rotate our image by 'rotation' degrees around the center of the image
    M = cv2.getRotationMatrix2D((cX, cY), rotation, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    # cv2.imshow("Rotated by" + str(rotation) + "degrees", rotated)
    # cv2.waitKey(0)
    return rotated
