import Rhino
import rhinoscriptsyntax as rs

from Robot import Robot

class TopographyPath():
    """Topography path generating class"""
    def __init__(self, mesh, intersect_num = 10, offset_dis = 3):
        self.mesh = mesh
        self.intersect_plane = None
        self.intersect_num = intersect_num # number of polylines to be generated
        self.offset_dis = offset_dis # polyline offset distance unit: mm

    def generatePolylineFrom3Pts(self, plane_constr_y, plane_constr_origin, plane_constr_x):
        # Create the first intersection plane, and flip the plane normal
        self.intersect_plane = self.planeFlipNormal(rs.PlaneFromPoints(plane_constr_origin, plane_constr_x, plane_constr_y))

        # generate the polylines from plane intersection
        polyline_point_array = self.polylineMeshPlaneIntersect(self.intersect_plane, self.intersect_num, self.offset_dis)
        return polyline_point_array

    def generatePolylineFromCentroidTopPt(self, top_point):
        """ function creates a plane with its normal from top point pointing to the mesh centroid"""
        # Compute the centroid of the mesh
        centroid_pts = rs.MeshAreaCentroid(self.mesh)
        # construct plane normal
        normal = rs.VectorCreate(centroid_pts, top_point)
        normal = rs.VectorUnitize(normal)
        # Create a plane
        self.intersect_plane = rs.PlaneFromNormal(top_point, normal)
        
        # generate the polylines from plane intersection
        polyline_point_array = self.polylineMeshPlaneIntersect(self.intersect_plane, self.intersect_num, self.offset_dis)
        return polyline_point_array

    def polylineMeshPlaneIntersect(self, intersect_plane, intersect_num, offset_distance):
        """generate polylines on mesh from intersection planes"""
        polyline_point_array = []
        for i in range(intersect_num):
            # Plane intersection on mesh
            polylines_intersect = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(self.mesh), intersect_plane)
            for result in polylines_intersect:
                # Add polyline into Rhino UI and append the intersection points
                polyline_point_array.append(rs.PolylineVertices(rs.AddPolyline(result)))
                
            # translate the intersect plane along its normal axis by a given distance
            xform = rs.XformTranslation(offset_distance*intersect_plane.ZAxis)
            intersect_plane = rs.PlaneTransform(intersect_plane, xform)
        return polyline_point_array

    def planeFlipNormal(self, plane):
        plane_rotated = rs.RotatePlane(plane, 180.0, plane.XAxis)
        return plane_rotated

    def exportPolylineCSV(self, polyline_list):
        """ export polyline points as *.cvs file"""
        #create a filename
        filename = rs.SaveFileName("Save CSV file","*.csv||", None, "topography", "csv")
        
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
        print "Exporting polyline points as CSV file successfully"
        
        #Close the file after writing!
        file.close()

    def exportPolylineGcode(self, polyline_list):
        """export polyline array points as gcode file"""
        robot = Robot()
        #create a filename
        filename = rs.SaveFileName("Save Gcode file","*.gcode||", None, "topography", "gcode")
        
        #open the file for writing
        file = open(filename, 'w')
        file.write("G21         ; Set units to mm\n")
        file.write("G90         ; Absolute positioning\n")
        file.write("M4 S0       ; Enable Laser (0 power)\n")
         
        # Gcode format
        for polyline in polyline_list:
            # Fast move to the first point of each polyline
            robot_joint = robot.inverseKinematics([polyline[0].X, polyline[0].Y, polyline[0].Z])
            line = "G0 X%.3f  Y%.3f  Z%.3f S0\n" %(robot_joint[0], robot_joint[1], robot_joint[2])
            file.write(line)
            file.write("G1 F3000    ; Feed rate\n")
            
            for pt in polyline[1:]:
                # print "x: %.4f, y: %.4f, z: %.4f" %(x,y,z)
                robot_joint = robot.inverseKinematics([pt.X, pt.Y, pt.Z])
                line = "X%.3f  Y%.3f  Z%.3f S500\n" %(robot_joint[0], robot_joint[1], robot_joint[2])
                file.write(line)
            file.write("-------\n")
            
        file.write("M5          ; Disable Laser")
        
        print ""
        print "G-code exported successfully!"
        
        #Close the file after writing!
        file.close()

    def transformPolylines(polyline_list, transform_matrix):
        """transform a polyline point array/list by the given transformation matrix"""
        polyline_transformed_list = []
        for polyline in polyline_list:
            polyline_transformed_list.append(rs.PointArrayTransform(polyline, transform_matrix))
        
        return polyline_transformed_list


if __name__ == "__main__":
    # Select the mesh
    mesh = rs.GetObject("Select mesh", rs.filter.mesh)
    
    # Generate topography path
    topographyObj = TopographyPath(mesh)

    # Select 3 vertex on the mesh to construct a intersection plane
    pt_1 = rs.GetPointOnMesh(mesh, "Select 1st vertice on mesh for constructing a plane")
    pt_2 = rs.GetPointOnMesh(mesh, "Select 2nd vertice on mesh for constructing a plane")
    pt_3 = rs.GetPointOnMesh(mesh, "Select 3rd vertice on mesh for constructing a plane")

    polyline_point_array = topographyObj.generatePolylineFrom3Pts(pt_1, pt_2, pt_3)
    
    ## Select a top vertice on the mesh to construct a plane normal
    # mesh_top_pt = rs.GetPointOnMesh(mesh, "Select a top vertice on mesh")
    # polyline_point_array = topographyObj.generatePolylineFromCentroidTopPt(mesh_top_pt)
    
    # Transform polyline point 
    #xform_2 = rs.XformRotation2(45.0, (0,0,1), (0,0,0))
    #polyline_point_array_transformed = transformPolylines(polyline_point_array, xform_2)
    #for polyline in polyline_point_array_transformed:
    #    rs.AddPolyline(polyline)
    
    # Exporting the points save as gcode file
    topographyObj.exportPolylineGcode(polyline_point_array)
#    print polyline_point_array