import rhinoscriptsyntax as rs
from myFunctions import*

# Select the mesh
mesh = rs.GetObject("Select mesh", rs.filter.mesh )

# Select 3 vertex on the mesh to construct a intersection plane
plane_constr_y = rs.GetPointOnMesh(mesh, "Select 1st vertice on mesh for constructing a plane")
plane_constr_origin = rs.GetPointOnMesh(mesh, "Select 2nd vertice on mesh for constructing a plane")
plane_constr_x = rs.GetPointOnMesh(mesh, "Select 3rd vertice on mesh for constructing a plane")

# Create the first intersection plane, then flip t
intersect_plane = planeFlipNormal(rs.PlaneFromPoints(plane_constr_origin, plane_constr_x, plane_constr_y))

intersect_num = 10 # number of polylines to be generated
offset_distance = 3 # polyline offset distance unit: mm

polyline_point_array = polylineMeshPlaneIntersect(mesh, intersect_plane, offset_distance, intersect_num)

for polyline in polyline_point_array:
    rs.AddPolyline(polyline)

# Transform polyline point 
#xform_2 = rs.XformRotation2(45.0, (0,0,1), (0,0,0))
#polyline_point_array_transformed = transformPolylines(polyline_point_array, xform_2)
#for polyline in polyline_point_array_transformed:
#    rs.AddPolyline(polyline)

## Exporting the points save as *.cvs file
#exportPolylinePoints(polyline_point_array)
