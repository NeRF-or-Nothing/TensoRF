import numpy as np
import json
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def polar_2_extrinsic(fps = 30, duration = 6, coefs = np.array([[1, 0], [np.pi/2, 0], [0, 1]])):
    #fps: frames per second
    #duration: duration of render in seconds

    #coefs: Matrix A produces translations and has three rows corresponding to r, theta, and phi in polar coordinates. Each column corresponds to the order of the function derivative.
    #All derivatives are normalized relative to duration.

    durations = np.full((coefs.shape[1]), duration)
    powers = np.arange(0, coefs.shape[1], 1)
    norm = np.power(duration, powers)

    r_c = coefs[0]
    theta_c = coefs[1]
    phi_c = coefs[2]

    r = lambda t: r_c[0] + (r_c[1]/duration)*t
    theta = lambda t: theta_c[0] + (2*np.pi*theta_c[1]/duration)*t
    phi = lambda t: phi_c[0] + (2*np.pi*phi_c[1]/duration)*t

    frame_times = np.linspace(0, 6, fps*duration)
    zeros = np.zeros(fps*duration)
    ones = np.ones(fps*duration)
    matrix = np.empty((4, 4, 180))

    #Note the extrinsic matrix is inverted relative to standard. It will map from camera to world coordinates.
    #see this link for reference: https://ksimek.github.io/2012/08/22/extrinsic/

    #s vector
    matrix[0][0] = np.sin(phi(frame_times))
    matrix[1][0] = -np.cos(phi(frame_times))
    matrix[2][0] = zeros

    #u vector
    matrix[0][1] = -np.cos(theta(frame_times))*np.cos(phi(frame_times))
    matrix[1][1] = -np.cos(theta(frame_times))*np.sin(phi(frame_times))
    matrix[2][1] = np.sin(theta(frame_times))

    #-L vector
    matrix[0][2] = -np.sin(theta(frame_times))*np.cos(phi(frame_times))
    matrix[1][2] = -np.sin(theta(frame_times))*np.sin(phi(frame_times))
    matrix[2][2] = -np.cos(theta(frame_times))

    #C vector
    matrix[0][3] = r(frame_times)*np.sin(theta(frame_times))*np.cos(phi(frame_times))
    matrix[1][3] = r(frame_times)*np.sin(theta(frame_times))*np.sin(phi(frame_times))
    matrix[2][3] = r(frame_times)*np.cos(theta(frame_times))

    #bottom row
    matrix[3][0] = zeros
    matrix[3][1] = zeros
    matrix[3][2] = zeros
    matrix[3][3] = ones

    matrix = np.moveaxis(matrix, 2, 0)

    return matrix

if __name__ == '__main__':

    matrices = polar_2_extrinsic()

    focal_len_scaled= 0.1
    aspect_ratio= 0.3

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(projection='3d')
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    for matrix in matrices:

        vertex_camera = np.array([[0, 0, 0, 1],
                                [focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                                [focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                                [-focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                                [-focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1]])

        vertex_transformed = vertex_camera @ matrix.T

        meshes = [[vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
                                [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
                                [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
                                [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
                                [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]]]
        ax.add_collection3d(Poly3DCollection(meshes, linewidths=0.3, alpha=0.15, color = 'red'))

    C = matrices[:, :, 3]
    C = np.moveaxis(C, 0, 1)
    ax.scatter(0, 0, 0, c = 'black', marker = '+', )
    ax.scatter(C[0], C[1], C[2], c = np.arange(len(C[0])))
    plt.show()