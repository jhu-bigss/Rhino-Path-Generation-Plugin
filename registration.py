from compas.utilities import XFunc

# Input: expects Nx3 matrix of points
# Returns R,t
# R = 3x3 rotation matrix
# t = 3x1 column vector

# import some Numpy functions
add = XFunc("numpy.add")
subtract = XFunc("numpy.subtract")
multiply = XFunc("numpy.multiply")
rand = XFunc('numpy.random.rand')
linalg_svd = XFunc('numpy.linalg.svd')
dot = XFunc("numpy.dot")
transpose = XFunc("numpy.transpose")
det = XFunc('numpy.linalg.det')
mean = XFunc('numpy.mean')
sum = XFunc("numpy.sum")
sqrt = XFunc("numpy.sqrt")

def rigid_transform_3D(A, B):
    assert len(A) == len(B)

    N = len(A); # total points

    centroid_A = mean(A, axis=0)
    centroid_B = mean(B, axis=0)
    
    # centre the points
    AA = subtract(A, centroid_A)
    BB = subtract(B, centroid_B)
    
    # dot is matrix multiplication for array
    H = dot(transpose(AA),BB)
    U, S, Vt = linalg_svd(H)
    # R = Vt.T * U.T
    R = dot(transpose(Vt),transpose(U))

    # special reflection case
    if det(R) < 0:
       print "Reflection detected"
       Vt[2][:] = [x*-1 for x in Vt[2]]
       R = dot(transpose(Vt),transpose(U))

    # t = -R*centroid_A.T + centroid_B.T
    t = subtract(transpose(centroid_B), dot(R, transpose(centroid_A)) )

    return R, t

def test_rigid_transform_3D():
    # Random rotation and translation
    R = rand(3,3)
    t = rand(3)
    
    # make R a proper rotation matrix, force orthonormal
    U, S, Vt = linalg_svd(R)
    R = dot(transpose(Vt),transpose(U))
    
    # remove reflection
    if det(R) < 0:
       Vt[2][:] = [x*-1 for x in Vt[2]]
       R = dot(transpose(Vt),transpose(U))
    
    # number of points
    n = 10
    
    A = rand(n,3);

    # B = R * A + t
    B = add(transpose(dot(R, transpose(A))), t)
    
    # recover the transformation
    ret_R, ret_t = rigid_transform_3D(A, B)
    
    A2 = add(transpose(dot(ret_R, transpose(A))), ret_t)
    
    # Find the error
    err = subtract(A2,B)
    
    err = multiply(err, err)
    err = sum(err)
    rmse = sqrt(err/n);
    
    print "Points A"
    print A
    print ""
    
    print "Points B"
    print B
    print ""
    
    print "Rotation"
    print R
    print ""
    
    print "Translation"
    print t
    print ""
    
    print "RMSE:", rmse
    print "If RMSE is near zero, the function is correct!"

if __name__ == "__main__":
    # Test with random data
    test_rigid_transform_3D()