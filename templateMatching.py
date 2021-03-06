import cv2
import numpy as np

# find all matches of the template in the image
# returns an array of (x, y) coordinate of the top/left point of each match
def getMatches(image, template, threshold):
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    # screen.showImage(result)
    loc = np.where(result >= threshold)
    results = zip(*loc[::-1])
    return results
    
# Highlight regions of interest in an image
def highlightRois(image, roisCoords, roiWidthHeight):
    rois = []
    for roiCoord in roisCoords:
        roiTopLeft = roiCoord['actualLoc']
        name = roiCoord['name']
        # extract the regions of interest from the image
        roiBottomRight = tuple([sum(x) for x in zip(roiTopLeft, roiWidthHeight)])
        roi = image[roiTopLeft[1]:roiBottomRight[1], roiTopLeft[0]:roiBottomRight[0]]
        rois.append({'topLeft': roiTopLeft, 'bottomRight': roiBottomRight, 'area': roi, 'name': name})

    # construct a darkened transparent 'layer' to darken everything
    # in the image except for the regions of interest
    mask = np.zeros(image.shape, dtype = "uint8")
    image = cv2.addWeighted(image, 0.25, mask, 0.75, 0)

    # put the original rois back in the image so that they look 'brighter'
    for roi in rois:
        image[roi['topLeft'][1]:roi['bottomRight'][1], roi['topLeft'][0]:roi['bottomRight'][0]] = roi['area']
        cv2.putText(image, roi['name'][0], roi['topLeft'], cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        
    return image