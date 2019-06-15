import Rhino
import rhinoscriptsyntax as rs
from myFunctions import*

# Select the mesh
mesh = rs.GetObject("Select mesh", rs.filter.mesh )

# Select 3 vertex on the mesh to construct a intersection plane
plane_constr_y = rs.GetPointOnMesh(mesh, "Select 1st vertice on mesh for constructing a plane")
plane_constr_origin = rs.GetPointOnMesh(mesh, "Select 2nd vertice on mesh for constructing a plane")
plane_constr_x = rs.GetPointOnMesh(mesh, "Select 3rd vertice on mesh for constructing a plane")

# Create the first intersection plane
intersect_plane = rs.PlaneFromPoints(plane_constr_origin, plane_constr_x, plane_constr_y)

polylines_num = 10 # number of polylines to be generated
polylines_offset_distance = -3 # offset distance unit: mm
polyline_array = []
for i in range(polylines_num):
    # Plane intersection on mesh
    polylines_intersect = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(mesh), intersect_plane)
    for result in polylines_intersect:
        polyline_array.append(result)
        # Add polyline into Rhino UI
        rs.AddPolyline(result)
    # translate the intersect plane along its normal axis by a given distance
    xform = rs.XformTranslation(polylines_offset_distance*intersect_plane.ZAxis)
    intersect_plane = rs.PlaneTransform(intersect_plane, xform)

print polyline_array