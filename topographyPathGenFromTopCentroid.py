import Rhino
import rhinoscriptsyntax as rs
from myFunctions import*

# Select the mesh
mesh = rs.GetObject("Select mesh", rs.filter.mesh )
# Compute the centroid of the mesh
centroid_pts = rs.AddPoint( rs.MeshAreaCentroid(mesh) )

# Select a vertice on the mesh to construct a vector
mesh_pts = rs.GetPointOnMesh(mesh, "Select a vertice on mesh")

# Create the first operation plane with norm vec (input1 -> input2)
intersect_plane = planeFrom2Pts(mesh_pts, centroid_pts)

polylines_num = 10 # number of polylines to be generated
polylines_offset_distance = 3 # offset distance unit: mm
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