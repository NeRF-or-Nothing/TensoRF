import numpy as np
import json
import sys
import matplotlib.pyplot as plt

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

    matrices = []
    t_step = 0
    for frame in range(0, fps*duration):

        matrix = np.zeros((3, 4))
        matrix[0][3] = x(t_step)
        matrix[1][3] = y(t_step)
        matrix[2][3] = z(t_step)

        matrices.append(matrix)
        t_step += 1/fps
    
    return np.array(matrices)

class CameraPoseVisualizer:
    def __init__(self, xlim, ylim, zlim):
        self.fig = plt.figure(figsize=(18, 7))
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_aspect("auto")
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_zlim(zlim)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')

        # Create axis
        axes = [3, 3, 3]
        
        # Create Data
        data = np.ones(axes)
        print(data.shape)
        
        # Control Transparency
        alpha = 0.01
        
        # Control colour
        colors = np.empty(axes + [4], dtype=np.float32)
        
        colors[:] = [1, 0, 0, alpha]  # red
        x,y,z = np.indices((4,4,4),dtype='float32')
        x-= 1.5
        y-= 1.5
        z-= 1.5
        self.ax.voxels(x,y,z,data, facecolors=colors, edgecolors='grey')
        print('initialize camera pose visualizer')

    def extrinsic2pyramid(self, extrinsic, color='r', focal_len_scaled=1, aspect_ratio=0.3):
        vertex_std = np.array([[0, 0, 0, 1],
                               [focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                               [focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                               [-focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                               [-focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1]])
        vertex_transformed = vertex_std @ extrinsic.T
        meshes = [[vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
                            [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]]]
        self.ax.add_collection3d(
            Poly3DCollection(meshes, facecolors=color, linewidths=0.3, edgecolors=color, alpha=0.15))

    def customize_legend(self, list_label):
        list_handle = []
        for idx, label in enumerate(list_label):
            color = plt.cm.rainbow(idx / len(list_label))
            patch = Patch(color=color, label=label)
            list_handle.append(patch)
        plt.legend(loc='right', bbox_to_anchor=(1.8, 0.5), handles=list_handle)

    def colorbar(self, max_frame_length):
        cmap = mpl.cm.rainbow
        norm = mpl.colors.Normalize(vmin=0, vmax=max_frame_length)
        self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), orientation='vertical', label='Frame Number')
    
    def plot_cam(self, cam, color="blue"):
        self.ax.scatter(cam[0],cam[1],cam[2], color= color)


    def show(self):
        print("Displaying Data")
        plt.title('Extrinsic Parameters')
        plt.show()

if __name__ == '__main__':

    matrices = polar_2_extrinsic(duration = 6, fps = 30)

    x = []
    y = []
    z = []
    for matrix in matrices:
        x.append(matrix[0][3])
        y.append(matrix[1][3])
        z.append(matrix[2][3])

    points = np.array([x, y, z])

    bruh = CameraPoseVisualizer(xlim = [-1,1], ylim = [-1,1], zlim = [-1,1])
    bruh.plot_cam(cam = points)
    plt.show()
