# dimensions of image
dimensions = [4032, 3024]
# chosen dimensions for image
imageDim = [3088, 2316]
# dimensions of padding added
padDim = [4032, 3024]
# base dimensions that relative x, y distances are calculated from
baseDim = [3088, 2316]
# NEEDS DONE, SET NECESSARY RELATIVE AREA TO SEARCH
areaToScanTopLeft = (0, 0)
areaToScanBottomRight = (4032, 3024)


def relXval(x):
    return int((x / baseDim[0]) * imageDim[0])


def relYval(y):
    return int((y / baseDim[1]) * imageDim[1])

def padImageDimDiff():
    diff = [0, 0]
    diff[0] = padDim[0] - imageDim[0]
    diff[1] = padDim[1] - imageDim[1]
    return diff

def setImageDimensions(dimensions):
    imageDim = dimensions
