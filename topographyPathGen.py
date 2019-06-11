import Rhino
import rhinoscriptsyntax as rs
from myFunctions import*

# Select the mesh
mesh = rs.GetObject("Select mesh", rs.filter.mesh )
# Compute the centroid of the mesh
centroid_pts = rs.AddPoint( rs.MeshAreaCentroid(mesh) )

# Select a vertice on the mesh to construct a vector
selected_indice = rs.GetPointOnMesh(mesh, "Select a vertice on mesh")
mesh_pts = rs.AddPoint( selected_indice )

# Create the first operation plane
op_plane = planeFrom2Pts(mesh_pts, centroid_pts)

iter_times = 10 # number of polylines to be generated
step_size = 3 # unit: mm
polyline_array = []
for i in range(iter_times):
    # Plane intersection on mesh
    polylines_intersect = Rhino.Geometry.Intersect.Intersection.MeshPlane(rs.coercemesh(mesh), op_plane)
    for result in polylines_intersect:
        polyline_array.append(result)
        # Add polyline into Rhino
        rs.AddPolyline(result)
    # translate the plane along its normal axis
    xform = rs.XformTranslation(step_size*op_plane.ZAxis)
    op_plane = rs.PlaneTransform(op_plane, xform)

print polyline_array