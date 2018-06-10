import numpy as np
from mayavi import mlab
from tvtk.api import tvtk


def ijk2xyz(ijk, affine):
    ijk1 = np.hstack((ijk, np.ones(len(ijk))[:, None]))
    return np.dot(affine, ijk1.T).T[:, :-1]

coords = np.load('coords_56.npy')
accuracies = np.load('accuracies_56.npy')
affine = np.load('affine.npy')

_2points = True

t_point1 = np.array([52, -18, 54])
t_point2 = np.array([42, -22, 54])

xyz_coords = ijk2xyz(coords, affine)

radius = 15

x = []
y = []
z = []
for c, a in zip(xyz_coords, accuracies.reshape(-1)):
    if np.array_equal(np.array(c), t_point1):
        i1 = a
    if _2points and np.array_equal(np.array(c), t_point2):
        i2 = a
    if a != 0 and c[2] == t_point1[2]:
        if abs(t_point1[0] - c[0]) <= radius and abs(t_point2[1] - c[1]) <= radius:
            x.append(c[0])
            y.append(c[1])
            z.append(a)

nt_point1 = np.copy(t_point1).astype("float32")
nt_point2 = np.copy(t_point2).astype("float32")

x = np.array(x)
y = np.array(y)
z = np.array(z)

ranges = [x.min(), x.max(), y.min(), y.max(), 0, 0]

nt_point1[0] -= x.min()
nt_point2[0] -= x.min()
x -= x.min()

nt_point1[1] -= y.min()
nt_point2[1] -= y.min()
y -= y.min()

s = z
nt_point1[2] = i1 - z.min()
if _2points:
    nt_point2[2] = i2 - z.min()
z = (z - z.min()) * 100
nt_point1[2] *= 100
nt_point2[2] *= 100

mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))

# Visualize the points
pts = mlab.points3d(x, y, z, s, scale_mode='none', scale_factor=0.2)

mlab.colorbar(orientation='vertical')

mlab.text3d(nt_point1[0], nt_point1[1], nt_point1[2] + 1, "%s" % t_point1)
if _2points:
    mlab.text3d(nt_point2[0], nt_point2[1], nt_point2[2] + 1, "%s" % t_point2)

# Create and visualize the mesh
mesh = mlab.pipeline.delaunay2d(pts)
mesh.filter.projection_plane_mode = 2
surf = mlab.pipeline.surface(mesh)

# Generate zome points.
x, y, z = np.mgrid[0:int(x.max()) + 1, 0:int(y.max()) + 1, 0:int(z.max()) + 1]

# The actual points.
pts = np.empty(z.shape + (3,), dtype=float)
pts[..., 0] = x
pts[..., 1] = y
pts[..., 2] = z

pts = pts.transpose((2, 1, 0, 3)).copy()
pts.shape = pts.size / 3, 3

sg = tvtk.StructuredGrid(dimensions=x.shape, points=pts)

d = mlab.pipeline.add_dataset(sg)
gx = mlab.pipeline.grid_plane(d)

gy = mlab.pipeline.grid_plane(d)
gy.grid_plane.axis = 'y'

gz = mlab.pipeline.grid_plane(d)
gz.grid_plane.axis = 'z'

axes = mlab.axes(nb_labels=50, y_axis_visibility=False, ranges=ranges)
axes.axes.font_factor = 0.5
axes._title_text_property.font_size = 6

x = np.arange(-50, 50, 10)
y = np.arange(-50, 50, 10)
z = np.arange(-50, 50, 10)
mlab.points3d(x, y, z, z, scale_mode='none', scale_factor=0.01)

streamline = mlab.pipeline.streamline(None, seedtype='point', color=(0, 0, 1))
# Tweak a bit the streamline.
streamline.stream_tracer.maximum_propagation = 100.
streamline.seed.widget.position = nt_point1

if _2points:
    streamline = mlab.pipeline.streamline(None, seedtype='point', color=(0, 0, 1))
    # Tweak a bit the streamline.
    streamline.stream_tracer.maximum_propagation = 100.
    streamline.seed.widget.position = nt_point2
mlab.show()
