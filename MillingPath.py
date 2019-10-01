import Rhino
from scriptcontext import doc
import rhinoscriptsyntax as rs
import math

from Robot import Robot

class MillingPath():
    """V line path generating class"""
    def __init__(self, mesh):
        self.mesh = mesh
        # self.mesh_centroid = rs.MeshAreaCentroid(self.mesh)
        self.beam_diameter = 1 # mm

    def generateMillingConstant(self):
        # Make sure to adjust the view to create correct construction plane
        bounding_box_vertices = rs.BoundingBox(self.mesh, view_or_plane = rs.ViewCPlane(), in_world_coords = True)
        origin = bounding_box_vertices[0]
        
        
        # Visulize the Bounding Box
        #rs.AddBox(bounding_box_vertices)
        #i = 0
        #for point in bounding_box_vertices:
        #    rs.AddPoint(point)
        #    rs.AddTextDot("%s" %i , point)
        #    i += 1
        
        
        # Create a coordinate frame on the bottom corner
        self.x_axis = rs.VectorCreate(bounding_box_vertices[1], origin)
        self.y_axis = rs.VectorCreate(bounding_box_vertices[3], origin)
        self.z_axis = rs.VectorCreate(bounding_box_vertices[4], origin)
        
        self.x_axis_bond_len = rs.VectorLength(self.x_axis)
        self.y_axis_bond_len = rs.VectorLength(self.y_axis)
        
        self.x_axis = rs.VectorUnitize(self.x_axis)
        self.y_axis = rs.VectorUnitize(self.y_axis)
        self.z_axis = rs.VectorUnitize(self.z_axis)
        
        #=================================
        # initialize X direction step size
        self.x_dir_step_count = math.floor(self.x_axis_bond_len/self.beam_diameter)
        x_dir_edge_margin = (self.x_axis_bond_len - self.x_dir_step_count * self.beam_diameter) / 2
        self.x_dir_step = rs.VectorScale(self.x_axis, (x_dir_edge_margin + self.beam_diameter/2) )
        
        # Create two intersection planes along x, y axes (method 1)
        # self.zy_intersect_plane = rs.PlaneFromFrame(origin, self.z_axis, self.y_axis)
        # self.zx_intersect_plane = rs.PlaneFromFrame(origin, self.z_axis, self.x_axis)
        # self.zy_intersect_plane = rs.PlaneTransform(self.zy_intersect_plane, rs.XformTranslation(self.x_dir_step))
        # polyline = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(self.mesh), self.zy_intersect_plane)
        
        # Create an intersection planes along x axis (method 2)
        zy_mesh_plane = rs.AddPlanarMesh(rs.AddCurve([bounding_box_vertices[0],bounding_box_vertices[4],bounding_box_vertices[7],bounding_box_vertices[3],bounding_box_vertices[0]],degree = 1))
        zy_mesh_plane = rs.TransformObject(zy_mesh_plane, rs.XformTranslation(self.x_dir_step))
        
        # Intersect mesh with a series of zy planes along x axis
        x_dir_polyline_list = []
        # Initial intersect mesh
        intersect_polyline = rs.MeshMeshIntersection(self.mesh, zy_mesh_plane)
        x_dir_polyline_list.append(intersect_polyline[0])
        # Adjust step size
        self.x_dir_step = rs.VectorScale(self.x_axis, self.beam_diameter)
        
        while len(x_dir_polyline_list) < self.x_dir_step_count:
            # intersect mesh
            intersect_polyline = rs.MeshMeshIntersection(self.mesh, zy_mesh_plane)
            x_dir_polyline_list.append( intersect_polyline[0] )
            # optional: add the polylline into the document
            doc.Objects.AddPolyline( intersect_polyline[0] )
            # forward one step
            zy_mesh_plane = rs.TransformObject(zy_mesh_plane, rs.XformTranslation(self.x_dir_step))
        # delete the intersection plane object
        rs.DeleteObject(zy_mesh_plane)
        
        #---------------------------------
        # initialize Y direction step size
        self.y_dir_step_count = math.floor(self.y_axis_bond_len/self.beam_diameter)
        y_dir_edge_margin = (self.y_axis_bond_len - self.y_dir_step_count * self.beam_diameter) / 2
        self.y_dir_step = rs.VectorScale(self.y_axis, (y_dir_edge_margin + self.beam_diameter/2) )
        
        # Create an intersection planes along y axis (method 2)
        zx_mesh_plane = rs.AddPlanarMesh(rs.AddCurve([bounding_box_vertices[0],bounding_box_vertices[1],bounding_box_vertices[5],bounding_box_vertices[4],bounding_box_vertices[0]],degree = 1))
        zx_mesh_plane = rs.TransformObject(zx_mesh_plane, rs.XformTranslation(self.y_dir_step))
        
        # Intersect mesh with a series of zy planes along y axis
        y_dir_polyline_list = []
        # Initial intersect mesh
        intersect_polyline = rs.MeshMeshIntersection(self.mesh, zx_mesh_plane)
        y_dir_polyline_list.append(intersect_polyline[0])
        # Adjust step size
        self.y_dir_step = rs.VectorScale(self.y_axis, self.beam_diameter)
        
        while len(y_dir_polyline_list) < self.y_dir_step_count:
            # intersect mesh
            intersect_polyline = rs.MeshMeshIntersection(self.mesh, zx_mesh_plane)
            y_dir_polyline_list.append( intersect_polyline[0] )
            # forward one step
            zx_mesh_plane = rs.TransformObject(zx_mesh_plane, rs.XformTranslation(self.y_dir_step))
        # delete the intersection plane object
        rs.DeleteObject(zx_mesh_plane)


if __name__ == "__main__":
    # Select the mesh
    mesh = rs.GetObject("Select mesh", rs.filter.mesh)
    
    # Generate Milling path
    MillingObj = MillingPath(mesh)
    milling_polyline = MillingObj.generateMillingConstant()
    
    # Exporting the points save as gcode file
#    MillingObj.exportMillingGcode(v_polyline)