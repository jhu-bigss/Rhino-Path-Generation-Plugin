import rhinoscriptsyntax as rs

def vectorFrom2PtsNormalized(point_2, point_1):
    """Create a normalized vector from given two points"""
    vector = rs.VectorCreate(point_2, point_1)
    vector = rs.VectorUnitize(vector)
    return vector

def planeFrom2Pts(point_1, point_2):
    """ function creates a plane from two given points, plane go through 1st point with normal vector (pt2 - pt1)"""
    # construct plane normal
    normal = vectorFrom2PtsNormalized(point_2, point_1)
    # Create a plane
    plane = rs.PlaneFromNormal(point_1, normal)
    
    return plane

