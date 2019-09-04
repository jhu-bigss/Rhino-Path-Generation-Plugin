import Rhino
import rhinoscriptsyntax as rs

from Robot import Robot

class VLinePath():
    """V line path generating class"""
    def __init__(self, mesh):
        self.mesh = mesh
        # self.mesh_centroid = rs.MeshAreaCentroid(self.mesh)

    def generateVLineFrom3Pts(self):
        # Select 3 vertex on the mesh to construct 2 intersection planes
        pt_center = rs.GetPointOnMesh(mesh, "Select top center point on mesh")
        pt_edge_1 = rs.GetPointOnMesh(mesh, "Select 1st edge point")
        # Optinal: reference lines
        ln_edge_1 = rs.AddLine(pt_center, pt_edge_1)
        vec_edge_1 = rs.VectorCreate(pt_edge_1, pt_center)
        pt_edge_2 = rs.GetPointOnMesh(mesh, "Select 2nd edge point")
        ln_edge_2 = rs.AddLine(pt_center, pt_edge_2)
        vec_edge_2 = rs.VectorCreate(pt_edge_2, pt_center)
        
        # constructive orthonormal plane
        plane_constr = rs.PlaneFromPoints(pt_center, pt_edge_1, pt_edge_2)
        intersect_plane_1 = rs.PlaneFromFrame(pt_center, plane_constr.ZAxis, vec_edge_1)
        intersect_plane_2 = rs.PlaneFromFrame(pt_center, plane_constr.ZAxis, vec_edge_2)
        
        # delete the reference lines
        rs.DeleteObject(ln_edge_1)
        rs.DeleteObject(ln_edge_2)
        
        # Plane intersection on mesh -> polylines
        polylines_intersect_1 = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(self.mesh), intersect_plane_1)[0]
        polylines_intersect_2 = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(self.mesh), intersect_plane_2)[0]
        
        # Remove the other half polyline points segmented by the center point
        center_index_1 = polylines_intersect_1.ClosestIndex(pt_center)
        polylines_intersect_1.RemoveRange(0, center_index_1 + 1)
        # Optinoal: smooth 0 = no smoothing, 1 = complete smoothing
        polylines_intersect_1.Smooth(1)
        v_polylines_1 = rs.AddPolyline(polylines_intersect_1)
        
        center_index_2 = polylines_intersect_2.ClosestIndex(pt_center)
        polylines_intersect_2.RemoveRange(0, center_index_2 + 1)
        polylines_intersect_2.Smooth(1)
        v_polylines_2 = rs.AddPolyline(polylines_intersect_2)
        
        # Combine two polylines into a new polyline
        v_polyline_vertices = rs.PolylineVertices(v_polylines_1)
        v_polyline_vertices.reverse()
        v_polyline_vertices.append(Rhino.Geometry.Point3d(pt_center))
        v_polyline_vertices.extend(rs.PolylineVertices(v_polylines_2))
        
        # Delete the original 2 polylines
        rs.DeleteObjects([v_polylines_1, v_polylines_2])
        v_polyline = rs.AddPolyline(v_polyline_vertices)
        
        return v_polyline

    def exportVLineCSV(self, polyline_list):
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

    def exportVLineGcode(self, polyline_list):
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


if __name__ == "__main__":
    # Select the mesh
    mesh = rs.GetObject("Select mesh", rs.filter.mesh)
    
    # Generate vline path
    vlineObj = VLinePath(mesh)
    v_polyline = vlineObj.generateVLineFrom3Pts()
    
    # Exporting the points save as gcode file
#    vlineObj.exportVLineGcode(v_polyline)