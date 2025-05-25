import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

from read_GIPS_distance import UWBpos  


def compute_gdop(anchors: np.ndarray, x_tag: float, y_tag: float) -> float:
    """
    Compute 2D GDOP for a given tag position (x_tag, y_tag).
    anchors: (3,2) array of anchor coordinates in same relative (meter) space.
    """
    diffs = anchors - np.array([x_tag, y_tag])
    dists = np.linalg.norm(diffs, axis=1)
    G = diffs / dists[:, None]       # Jacobian (direction cosines)
    Q = np.linalg.inv(G.T @ G)       # covariance matrix factor
    return np.sqrt(np.trace(Q))


def generate_gdop_heatmap(anchors: np.ndarray,
                          margin: float = 1.0,
                          step: float = 0.5,
                          output_file: str = 'gdop_heatmap.png'):
    """
    Generates and saves a GDOP heatmap over a grid covering the anchor area.
    anchors: (3,2) array of anchor relative positions (meters).
    margin: extra meters around min/max anchor coords to include.
    step: grid resolution in meters.
    """
    # grid boundaries
    xmin, xmax = anchors[:, 0].min() - margin, anchors[:, 0].max() + margin
    ymin, ymax = anchors[:, 1].min() - margin, anchors[:, 1].max() + margin

    xs = np.arange(xmin, xmax + step, step)
    ys = np.arange(ymin, ymax + step, step)
    grid_x, grid_y = np.meshgrid(xs, ys)

    gdop_map = np.zeros_like(grid_x)
    for i in range(grid_x.shape[0]):
        for j in range(grid_x.shape[1]):
            gdop_map[i, j] = compute_gdop(anchors, grid_x[i, j], grid_y[i, j])

    # plot and save
    plt.figure(figsize=(6,5))
    plt.imshow(
        gdop_map,
        origin='lower',
        extent=(xmin, xmax, ymin, ymax),
        aspect='equal'
    )
    plt.scatter(anchors[:,0], anchors[:,1], c='red', marker='x', label='Anchors')
    plt.colorbar(label='GDOP')
    plt.legend(loc='upper right')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('2D GDOP Heatmap')
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"GDOP heatmap saved to {output_file}")


def main():
    # instantiate your UWB positioning class
    uwb = UWBpos()

    # optional: read distances and compute tag position
    # distances = uwb.UWB_read()
    # x_tag_rel, y_tag_rel = uwb.compute_relative()
    # print(f"Measured tag relative position (m): {x_tag_rel:.2f}, {y_tag_rel:.2f}")

    # get anchor relative positions (meters)
    anchors = np.vstack((uwb.X, uwb.Y)).T  # shape (3,2)

    # generate and save GDOP heatmap
    generate_gdop_heatmap(
        anchors=anchors,
        margin=1.0,
        step=0.5,
        output_file='gdop_heatmap1.png'
    )


if __name__ == '__main__':
    main()
