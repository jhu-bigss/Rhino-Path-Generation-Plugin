import Rhino
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

def planeFlipNormal(plane):
    plane_rotated = rs.RotatePlane(plane, 180.0, plane.XAxis)
    return plane_rotated

def polylineMeshPlaneIntersect(mesh, intersect_plane, offset_distance = 3, intersect_num = 10):
    """generate polylines on mesh from intersection planes"""
    polyline_point_array = []
    for i in range(intersect_num):
        # Plane intersection on mesh
        polylines_intersect = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(mesh), intersect_plane)
        for result in polylines_intersect:
            # Add polyline into Rhino UI and append the intersection points
            polyline_point_array.append(rs.PolylineVertices(rs.AddPolyline(result)))
            
        # translate the intersect plane along its normal axis by a given distance
        xform = rs.XformTranslation(offset_distance*intersect_plane.ZAxis)
        intersect_plane = rs.PlaneTransform(intersect_plane, xform)
    return polyline_point_array       

def exportPolylinePoints(polyline_list):
    """ export polyline points as *.cvs file"""
    #create a filename variable
    filename = rs.SaveFileName("Save CSV file","*.csv||", None, "ptExport", "csv")
    
    #open the file for writing
    file = open(filename, 'w')
    
    #create and write a headerline for our CSV
    headerline = "X,Y,Z\n"
    file.write(headerline)
     
    #print all pts
    i = 1 #polyline counter
    for polyline in polyline_list:
        line = "polyline: %d\n" %(i)
        i += 1
        file.write(line)
        for pt in polyline:
            x = pt.X
            y = pt.Y
            z = pt.Z
            # print "x: %.4f, y: %.4f, z: %.4f" %(x,y,z)
            line = "%.4f,%.4f,%.4f \n" %(x,y,z)
            file.write(line)
    print "Exporting polyline points completed"
    #Close the file after writing!
    file.close()
    return


def transformPolylines(polyline_list, transform_matrix):
    """transform a polyline point array/list by the given transformation matrix"""
    polyline_transformed_list = []
    for polyline in polyline_list:
        polyline_transformed_list.append(rs.PointArrayTransform(polyline, transform_matrix))
    
    return polyline_transformed_list
