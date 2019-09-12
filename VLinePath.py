import Rhino
import rhinoscriptsyntax as rs

from Robot import Robot

class VLinePath():
    """V line path generating class"""
    def __init__(self, mesh):
        self.mesh = mesh
        self.polyline = None
        self.show_ref_line_during_operation = True

    def generateVLineFrom3Pts(self):
        """generate a vline path on mesh by selecting 3 points"""
        
        # first, select 3 vertex on the mesh to construct 2 intersection planes
        pt_center = rs.GetPointOnMesh(self.mesh, "Select top center point on mesh")
        pt_edge_1 = rs.GetPointOnMesh(self.mesh, "Select 1st edge point")
        
        if self.show_ref_line_during_operation is True:
            edge_1 = rs.AddLine(pt_center, pt_edge_1)
            
        vec_edge_1 = rs.VectorCreate(pt_edge_1, pt_center)
        pt_edge_2 = rs.GetPointOnMesh(self.mesh, "Select 2nd edge point")
        
        if self.show_ref_line_during_operation is True:
            edge_2 = rs.AddLine(pt_center, pt_edge_2)
            
        vec_edge_2 = rs.VectorCreate(pt_edge_2, pt_center)
        
        # Using constructive orthonormal plane to generate two addtional planes for intersection
        constr_plane = rs.PlaneFromPoints(pt_center, pt_edge_1, pt_edge_2)
        intersect_plane_1 = rs.PlaneFromFrame(pt_center, constr_plane.ZAxis, vec_edge_1)
        intersect_plane_2 = rs.PlaneFromFrame(pt_center, constr_plane.ZAxis, vec_edge_2)
        
        # delete the reference lines
        if self.show_ref_line_during_operation is True:
            rs.DeleteObjects([edge_1, edge_2])
        
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
        
        # Combine two polylines into one polyline
        v_polyline_vertices = rs.PolylineVertices(v_polylines_1)
        v_polyline_vertices.reverse() # reverse the 1st polyline
        v_polyline_vertices.append(Rhino.Geometry.Point3d(pt_center)) # append the central point
        v_polyline_vertices.extend(rs.PolylineVertices(v_polylines_2)) # append the 2nd polyline
        rs.DeleteObjects([v_polylines_1, v_polylines_2]) # Delete the original 2 polylines
        
        # Save the new single polyline
        self.polyline = v_polyline_vertices
        
        return self.polyline

    def exportCSV(self, polyline_list):
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

    def exportGcode(self):
        """export polyline array points as gcode file"""
        if self.polyline is None:
            raise TypeError("Generate polyline first before exporting Gcode.")
        
        robot = Robot()
        laser_power = 500
        #create a filename
        filename = rs.SaveFileName("Save Gcode file","*.gcode||", None, "vline", "gcode")
        
        #open the file for writing
        file = open(filename, 'w')
        file.write("G21         ; Set units to mm\n")
        file.write("G90         ; Absolute positioning\n")
        file.write("M4 S0       ; Enable Laser (0 power)\n")
         
        # Gcode formating
        # first, move to the first point
        robot_joint = robot.inverseKinematics([self.polyline[0][0], self.polyline[0][1], self.polyline[0][2]])
        file.write("G0 X%.3f  Y%.3f  Z%.3f S0\n" %(robot_joint[0], robot_joint[1], robot_joint[2]))
        file.write("G1 F3000    ; Feed rate\n")
        
        for vertice in self.polyline[1:]:
            robot_joint = robot.inverseKinematics([vertice[0], vertice[1], vertice[2]])
            line = "G1 X%.3f  Y%.3f  Z%.3f S%d\n" %(robot_joint[0], robot_joint[1], robot_joint[2], laser_power)
            file.write(line)
            file.write("-------\n")
        
        # Life up laser head
        file.write("G0 X%.3f  Y%.3f  Z%.3f S0\n" %(robot_joint[0], robot_joint[1], 0))
        file.write("M5          ; Disable Laser")
        
        print ""
        print "G-code exported successfully!"
        
        #Close the file after writing!
        file.close()

if __name__ == "__main__":
    # Select the mesh
    mesh = rs.GetObject("Select mesh", rs.filter.mesh)
    
    # Generate vline path on mesh
    vlineObj = VLinePath(mesh)
    v_polyline = rs.AddPolyline(vlineObj.generateVLineFrom3Pts())
    
    # Exporting the polyline as gcode file
    vlineObj.exportGcode()