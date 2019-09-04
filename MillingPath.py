import Rhino
import rhinoscriptsyntax as rs

from Robot import Robot

class MillingPath():
    """V line path generating class"""
    def __init__(self, mesh):
        self.mesh = mesh
        # self.mesh_centroid = rs.MeshAreaCentroid(self.mesh)
        self.slice_dist = 1 # mm

    def generateMillingConstant(self):
        # Make sure set the CPlane before running this function
        bounding_box_vertices = rs.BoundingBox(self.mesh, view_or_plane = rs.ViewCPlane(), in_world_coords = True)
        i = 0
        for point in bounding_box_vertices:
            rs.AddPoint(point)
            rs.AddTextDot("%s" %i , point)
            i += 1
        
        # Create coordinates system
        self.coord_sys = 
        
        # Construct slicing plane Y-Z
        
        # Slice along X axis
        
        # Construct slicing plane X-Z
        
        # Slice along Y axis
        
        # Slice the mesh
        
        
    def sliceAlongXAxis


if __name__ == "__main__":
    # Select the mesh
    mesh = rs.GetObject("Select mesh", rs.filter.mesh)
    
    # Generate Milling path
    MillingObj = MillingPath(mesh)
    milling_polyline = MillingObj.generateMillingConstant()
    
    # Exporting the points save as gcode file
#    MillingObj.exportMillingGcode(v_polyline)