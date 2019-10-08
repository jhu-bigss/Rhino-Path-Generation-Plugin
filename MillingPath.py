import Rhino
from scriptcontext import doc
import rhinoscriptsyntax as rs

from Robot import Robot

class MillingPath():
    """V line path generating class"""
    def __init__(self, mesh):
        self.mesh = mesh
        # self.mesh_centroid = rs.MeshAreaCentroid(self.mesh)
        self.beam_diameter = 0.4 # mm
        self.pocket_edge_margin = 0 # set 0 or 1/2 of the beam diameter
        self.layer_depth = 2 # mm
        self.layer_count = 8

    def generateMillingConstantDepth(self):
        # Bonding Box
        # Note: make sure to adjust the view to create correct construction plane
        # Or using current world coordinate
        bounding_box_vertices = rs.BoundingBox(self.mesh, view_or_plane = rs.ViewCPlane(), in_world_coords = True)
        
        # --- Visulize the Bounding Box ---
        #rs.AddBox(bounding_box_vertices)
        #i = 0
        #for point in bounding_box_vertices:
        #    rs.AddPoint(point)
        #    rs.AddTextDot("%s" %i , point)
        #    i += 1
        
        # Establish a coordinate frame on the bottom corner
        x_axis = rs.VectorCreate(bounding_box_vertices[1], bounding_box_vertices[0])
        y_axis = rs.VectorCreate(bounding_box_vertices[3], bounding_box_vertices[0])
        z_axis = rs.VectorCreate(bounding_box_vertices[4], bounding_box_vertices[0])
        
        x_axis_bond_len = rs.VectorLength(x_axis)
        y_axis_bond_len = rs.VectorLength(y_axis)
        
        x_axis = rs.VectorUnitize(x_axis)
        y_axis = rs.VectorUnitize(y_axis)
        z_axis = rs.VectorUnitize(z_axis)
        
        #======= SLICE ALONG X AXIS ======
        x_dir_polyline_list = []
        
        # initialize X direction step size
        x_dir_step_count = int(x_axis_bond_len/self.beam_diameter)
        x_dir_edge_remainder = (x_axis_bond_len - x_dir_step_count * self.beam_diameter) / 2
        x_dir_step = rs.VectorScale(x_axis, (x_dir_edge_remainder + self.pocket_edge_margin) )
        
        # Create two intersection planes along x, y axes (method 1)
        # self.zy_intersect_plane = rs.PlaneFromFrame(origin, z_axis, y_axis)
        # self.zx_intersect_plane = rs.PlaneFromFrame(origin, z_axis, x_axis)
        # self.zy_intersect_plane = rs.PlaneTransform(self.zy_intersect_plane, rs.XformTranslation(x_dir_step))
        # polyline = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(self.mesh), self.zy_intersect_plane)
        
        # Create an intersection planes along x axis (method 2)
        zy_plane_curve = rs.AddCurve([bounding_box_vertices[0],bounding_box_vertices[4],bounding_box_vertices[7],bounding_box_vertices[3],bounding_box_vertices[0]],degree = 1)
        zy_mesh_plane = rs.AddPlanarMesh(zy_plane_curve)
        zy_mesh_plane = rs.TransformObject(zy_mesh_plane, rs.XformTranslation(x_dir_step))
        
        # Initial intersect mesh
        intersect_polyline = rs.MeshMeshIntersection(self.mesh, zy_mesh_plane)
        x_dir_polyline_list.append(intersect_polyline[0])
        # Adjust step size
        x_dir_step = rs.VectorScale(x_axis, self.beam_diameter)
        
        # Intersect mesh with a series of zy planes along x axis
        for x in range(x_dir_step_count):
            # forward one step
            zy_mesh_plane = rs.TransformObject(zy_mesh_plane, rs.XformTranslation(x_dir_step))
            # intersect mesh
            intersect_polyline = rs.MeshMeshIntersection(self.mesh, zy_mesh_plane)
            x_dir_polyline_list.append( intersect_polyline[0] )
            
        # delete the intersection plane curve & mesh object
        rs.DeleteObject(zy_plane_curve)
        rs.DeleteObject(zy_mesh_plane)
        
        #======= SLICE ALONG Y AXIS ======
        y_dir_polyline_list = []
        
        # initialize Y direction step size
        y_dir_step_count = int(y_axis_bond_len/self.beam_diameter)
        y_dir_edge_remainder = (y_axis_bond_len - y_dir_step_count * self.beam_diameter) / 2
        y_dir_step = rs.VectorScale(y_axis, (y_dir_edge_remainder + self.pocket_edge_margin) )
        
        # Create an intersection planes along y axis (method 2)
        zx_plane_curve = rs.AddCurve([bounding_box_vertices[0],bounding_box_vertices[1],bounding_box_vertices[5],bounding_box_vertices[4],bounding_box_vertices[0]],degree = 1)
        zx_mesh_plane = rs.AddPlanarMesh(zx_plane_curve)
        zx_mesh_plane = rs.TransformObject(zx_mesh_plane, rs.XformTranslation(y_dir_step))
        
        # Initial intersect mesh
        intersect_polyline = rs.MeshMeshIntersection(self.mesh, zx_mesh_plane)
        y_dir_polyline_list.append(intersect_polyline[0])
        # Adjust step size
        y_dir_step = rs.VectorScale(y_axis, self.beam_diameter)
        
        # Intersect mesh with a series of zy planes along y axis
        for x in range(y_dir_step_count):
            # forward one step
            zx_mesh_plane = rs.TransformObject(zx_mesh_plane, rs.XformTranslation(y_dir_step))
            # intersect mesh
            intersect_polyline = rs.MeshMeshIntersection(self.mesh, zx_mesh_plane)
            y_dir_polyline_list.append( intersect_polyline[0] )
            
        # delete the intersection plane curve & mesh object
        rs.DeleteObject(zx_plane_curve)
        rs.DeleteObject(zx_mesh_plane)
        
        
        #==== STACK ALONG Z AXIS ====
        z_dir_polyline_list = []  # an empty 2-dimensional list
        
        # initialize negative Z direction step size
        z_dir_step = rs.VectorScale(z_axis, - self.layer_depth)
        # loop through and translate each layer
        for n in range(self.layer_count):
            transformed_layer = []
            # alternate crossing
            if n % 2 == 0:
                for polyline in x_dir_polyline_list:
                    polyline = rs.PointArrayTransform(polyline, rs.XformTranslation(n * z_dir_step))
                    transformed_layer.append(polyline)
            else:
                for polyline in y_dir_polyline_list:
                    polyline = rs.PointArrayTransform(polyline, rs.XformTranslation(n * z_dir_step))
                    transformed_layer.append(polyline)
            z_dir_polyline_list.append(transformed_layer)
         
        return z_dir_polyline_list
         
#        mesh_border_curve = rs.DuplicateMeshBorder(self.mesh)
#        print mesh_border_curve


    def generateMillingFlatBottom(self):
        # Bonding Box
        bounding_box_vertices = rs.BoundingBox(self.mesh, view_or_plane = rs.ViewCPlane(), in_world_coords = True)
        
        # Establish a coordinate frame on the bottom corner
        x_axis = rs.VectorCreate(bounding_box_vertices[1], bounding_box_vertices[0])
        y_axis = rs.VectorCreate(bounding_box_vertices[3], bounding_box_vertices[0])
        z_axis = rs.VectorCreate(bounding_box_vertices[4], bounding_box_vertices[0])
        
        x_axis_bond_len = rs.VectorLength(x_axis)
        y_axis_bond_len = rs.VectorLength(y_axis)
        
        x_axis = rs.VectorUnitize(x_axis)
        y_axis = rs.VectorUnitize(y_axis)
        z_axis = rs.VectorUnitize(z_axis)
        
        
        # ==== SLICE ALONG Z AXIS ====
        z_dir_curve_list = []  # a curve list of guid
        
        # initialize negative Z direction step size
        z_dir_step = rs.VectorScale(z_axis, - self.layer_depth)
        
        # Create intersection mesh plane along z axis
        xy_plane_curve = rs.AddCurve([bounding_box_vertices[4],bounding_box_vertices[5],bounding_box_vertices[6],bounding_box_vertices[7],bounding_box_vertices[4]],degree = 1)
        xy_mesh_plane = rs.AddPlanarMesh(xy_plane_curve)
        
        # loop through each layer to find intersection area
        for x in range(self.layer_count):
            # Move one step down the intersect plane
            xy_mesh_plane = rs.TransformObject(xy_mesh_plane, rs.XformTranslation(z_dir_step))
            # intersect mesh, add curve into rhino document
            intersect_polyline = rs.MeshMeshIntersection(self.mesh, xy_mesh_plane)
            z_dir_curve_list.append(rs.AddCurve(intersect_polyline[0]))
            
            #intersect_polyline_obj = rs.AddPolyline(intersect_polyline[0])
            #z_dir_mesh_plane_list.append( rs.MeshPolyline(intersect_polyline_obj) )
            #rs.DeleteObject(intersect_polyline_obj)
            
        # delete the intersection plane curve & mesh object
        rs.DeleteObject(xy_plane_curve)
        rs.DeleteObject(xy_mesh_plane)
        
        
        # ==== SLICE ALONG X,Y AXES ====
        # initialize an empty 2-dimensional list
        z_dir_polyline_list = []
        for n in range(self.layer_count):
            z_dir_polyline_list.append([])
        
        # initialize x direction step size
        x_dir_step_count = int(x_axis_bond_len/self.beam_diameter)
        x_dir_edge_remainder = (x_axis_bond_len - x_dir_step_count * self.beam_diameter) / 2
        x_dir_step = rs.VectorScale(x_axis, (x_dir_edge_remainder + self.pocket_edge_margin) )
        
        # initialize y direction step size
        y_dir_step_count = int(y_axis_bond_len/self.beam_diameter)
        y_dir_edge_remainder = (y_axis_bond_len - y_dir_step_count * self.beam_diameter) / 2
        y_dir_step = rs.VectorScale(y_axis, (y_dir_edge_remainder + self.pocket_edge_margin) )
        
        # create intersection plane along x axis
        zy_plane = rs.PlaneFromFrame(bounding_box_vertices[0], z_axis, y_axis)
        zy_plane = rs.PlaneTransform(zy_plane, rs.XformTranslation(x_dir_step) )
        
        # create intersection plane along y axis
        zx_plane = rs.PlaneFromFrame(bounding_box_vertices[0], z_axis, x_axis)
        zx_plane = rs.PlaneTransform(zx_plane, rs.XformTranslation(y_dir_step) )
        
        # Initial intersect
        for n, curve in enumerate(z_dir_curve_list):
            # alternate crossing
            if n % 2 == 0:
                result = rs.PlaneCurveIntersection(zy_plane, curve)
                if result is not None:
                    z_dir_polyline_list[n].append([result[0][1], result[-1][1]])
            else:
                result = rs.PlaneCurveIntersection(zx_plane, curve)
                if result is not None:
                    z_dir_polyline_list[n].append([result[0][1], result[-1][1]])
            
        # Adjust step size
        x_dir_step = rs.VectorScale(x_axis, self.beam_diameter)
        y_dir_step = rs.VectorScale(y_axis, self.beam_diameter)
        
        # Intersect mesh with a series of zy planes along y axis
        for x in range(max(x_dir_step_count, y_dir_step_count)):
            zy_plane = rs.PlaneTransform(zy_plane, rs.XformTranslation(x_dir_step) )
            zx_plane = rs.PlaneTransform(zx_plane, rs.XformTranslation(y_dir_step) )
            # look through all the curves to find intersection points
            for n, curve in enumerate(z_dir_curve_list):
                # alternate crossing
                if n % 2 == 0:
                    result = rs.PlaneCurveIntersection(zy_plane, curve)
                    if result is not None:
                       if len(result) > 3:
                            z_dir_polyline_list[n].append([result[0][1],result[-1][1]])
                            z_dir_polyline_list[n].append([result[1][1],result[-2][1]])
                       else:
                            z_dir_polyline_list[n].append([result[0][1],result[-1][1]])
                else:
                    result = rs.PlaneCurveIntersection(zx_plane, curve)
                    if result is not None:
                       if len(result) > 3:
                            z_dir_polyline_list[n].append([result[0][1],result[-1][1]])
                            z_dir_polyline_list[n].append([result[1][1],result[-2][1]])
                       else:
                            z_dir_polyline_list[n].append([result[0][1],result[-1][1]]) 
                    
        # delete the z-level curves
        rs.DeleteObjects(z_dir_curve_list)
        
        return z_dir_polyline_list


    def addPath2RhinoDoc4Display(self, path_bundle):
        # Add to the Rhino document for display
        # input: path_bundle - 2 dimensional path layers of polyline lists
        for layer in path_bundle:
            for polyline in layer:
                doc.Objects.AddPolyline( polyline )


if __name__ == "__main__":
    # Select the mesh
    mesh = rs.GetObject("Select mesh", rs.filter.mesh)
    
    # Generate Milling path
    milling_obj = MillingPath(mesh)
    #milling_polyline = MillingObj.generateMillingConstantDepth()
    
    path_bundle = milling_obj.generateMillingFlatBottom()
    milling_obj.addPath2RhinoDoc4Display(path_bundle)
    
    # Exporting the points save as gcode file
#    MillingObj.exportMillingGcode(v_polyline)