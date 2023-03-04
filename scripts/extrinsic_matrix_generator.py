import numpy as np
import json
import sys
import matplotlib.pyplot as plt
from scipy.special import factorial
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def polar_2_extrinsic(fps = 30, duration = 6, coefs = np.array([[1, 0], [np.pi/2, 0], [0, 1]])):
    #fps: frames per second
    #duration: duration of render in seconds

    #coefs: Matrix A produces translations and has three rows corresponding to r, theta, and phi in polar coordinates. Each column corresponds to the order of the function derivative.
    #All derivatives are normalized relative to duration.

    l = coefs.shape[1]
    r_norm = (1/factorial(np.arange(0, l, 1)))*np.power((1/duration), np.arange(0, l, 1))
    rad_norm = 2*np.pi*(1/factorial(np.arange(0, l, 1)))*np.power((1/duration), np.arange(0, l, 1))
    rad_norm[0] = 1

    zeros = np.zeros(fps*duration)
    ones = np.ones(fps*duration)
    matrix = np.empty((4, 4, fps*duration))

    times = np.full((l, fps*duration), np.linspace(0, duration, fps*duration)).T
    times = np.power(times, np.arange(0, l, 1))

    r = np.sum(r_norm*coefs[0]*times, axis = 1)
    theta = np.sum(rad_norm*coefs[1]*times, axis = 1)
    phi = np.sum(rad_norm*coefs[2]*times, axis = 1)

    #Note the extrinsic matrix is inverted relative to standard. It will map from camera to world coordinates.
    #see this link for reference: https://ksimek.github.io/2012/08/22/extrinsic/

    #s vector
    matrix[0][0] = np.sin(phi)
    matrix[1][0] = -np.cos(phi)
    matrix[2][0] = zeros

    #u vector
    matrix[0][1] = -np.cos(theta)*np.cos(phi)
    matrix[1][1] = -np.cos(theta)*np.sin(phi)
    matrix[2][1] = np.sin(theta)

    #-L vector
    matrix[0][2] = -np.sin(theta)*np.cos(phi)
    matrix[1][2] = -np.sin(theta)*np.sin(phi)
    matrix[2][2] = -np.cos(theta)

    #C vector
    matrix[0][3] = r*np.sin(theta)*np.cos(phi)
    matrix[1][3] = r*np.sin(theta)*np.sin(phi)
    matrix[2][3] = r*np.cos(theta)

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