import numpy as np
import json
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def polar_2_extrinsic(fps = 30, duration = 6, coefs = np.array([[[1, 0], [np.pi/2, 0], [0, 1]], [[0, 0], [0, 0], [0, 0]]])):
    #fps: frames per second
    #duration: duration of render in seconds

    #coefs: First 3x2 matrix procudes translations has three rows corresponding to r, theta, and phi in polar coordinates. Each column contains starting and first
    #derivative information for each of these parameters. The second 3x2 matrix contains the same information form camera rotations. The camera rotations are relative to the origin
    #of the coordinate system.

        #r_0: initial radius value
        #r_1: augmentation of radius value at the end of the duration

        #theta_0: initial polar angle in radians
        #theta_1: change in polar angle in number of complete rotations for given duration

        #phi_0: initial azimuthal angle in radians
        #phi_1: change in azimuthal angle in number of complete rotations for given duration

    n = fps*duration

    r_c = coefs[0][0]
    theta_c = coefs[0][1]
    phi_c = coefs[0][2]

    r = lambda t: r_c[0] + (r_c[1]/duration)*t
    theta = lambda t: theta_c[0] + (2*np.pi*theta_c[1]/duration)*t
    phi = lambda t: phi_c[0] + (2*np.pi*phi_c[1]/duration)*t

    #x = r sin(theta) cos(phi)
    #y = r sin(theta) sin(phi)
    #z = r cos(theta)
    x = lambda t: r(t)*np.sin(theta(t))*np.cos(phi(t))
    y = lambda t: r(t)*np.sin(theta(t))*np.sin(phi(t))
    z = lambda t: r(t)*np.cos(theta(t))

    frame_times = np.linspace(0, 6, fps*duration)
    x_v = x(frame_times)
    y_v = y(frame_times)
    z_v = z(frame_times)

    zeros = np.zeros(fps*duration)
    ones = np.ones(fps*duration)

    C = np.array([x_v, y_v, z_v])
    C = np.moveaxis(C, 0, 1)

    L = C.copy()
    L /= np.linalg.norm(L)

    u = np.array([zeros, ones, zeros])
    u = np.moveaxis(u, 0, 1)

    s = np.cross(L, u)
    s /= np.linalg.norm(s)

    u = np.cross(s, L)

    R = np.array([[s[:, 0], s[:, 1], s[:, 2]], 
                    [u[:, 0], u[:, 1], u[:, 2]], 
                    [-L[:, 0], -L[:, 1], -L[:, 2]]])
    R = np.moveaxis(R, 2, 0)

    t = []
    i = 0
    for matrix in R:
        t.append(-matrix @ C[i])
        i += 1

    t = np.array(t)

    matrix = np.array([
        [s[:, 0], s[:, 1], s[:, 2], t[:, 0]],
        [u[:, 0], u[:, 1], u[:, 2], t[:, 1]],
        [-L[:, 0], -L[:, 1], -L[:, 2], t[:, 2]],
        [zeros, zeros, zeros, ones]
    ])
    matrix = np.moveaxis(matrix, 2, 0)

    return matrix, C, R, t

if __name__ == '__main__':

    matrices, C, R, t = polar_2_extrinsic()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection='3d')
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    points = np.moveaxis(C, 0, 1)
    ax.scatter(0, 0, 0, c = 'black')
    ax.scatter(points[0], points[1], points[2], c = np.arange(len(points[0])))

    focal_len_scaled=1
    aspect_ratio=0.3

    for matrix in matrices:

        vertex_std = np.array([[0, 0, 0, 1],
                                [focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                                [focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                                [-focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                                [-focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1]])

        vertex_transformed = vertex_std @ matrix.T

        meshes = [[vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
                                [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
                                [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
                                [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
                                [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]]]
        ax.add_collection3d(Poly3DCollection(meshes, linewidths=0.3, alpha=0.15))

    plt.show()