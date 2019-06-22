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

intersect_num = 10 # number of polylines to be generated
offset_distance = 3 # polyline offset distance unit: mm

polyline_point_array = polylineMeshPlaneIntersect(mesh, intersect_plane, offset_distance, intersect_num)

print polyline_point_array