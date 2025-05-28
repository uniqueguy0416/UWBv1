#!/usr/bin/env python3
import os
import serial
import numpy as np
import pandas as pd

class UWB3DLocal:
    def __init__(self, anchor_ids, anchor_positions, port='/dev/ttyUSB0', baud=57600):
        """
        anchor_ids:      list of anchor IDs, e.g. ['0241…','0341…','0441…','0541…']
        anchor_positions:list of (x,y,z) tuples in meters, same order as anchor_ids
        """
        assert len(anchor_ids) == len(anchor_positions), "ID 與座標數量必須相同"
        self.anchor_ids = anchor_ids
        self.anchors = np.array(anchor_positions, dtype=float)  # shape (m,3)
        self.dists   = np.zeros(len(anchor_ids), dtype=float)   # measured distances (m)
        # initialize serial port
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            print(f"Connected to {port} at {baud} baud")
        except Exception as e:
            print(f"Cannot open serial port {port}: {e}")
            self.ser = None

    def UWB_read(self):
        """Read one round of distances for all anchors and fill self.dists"""
        if self.ser is None:
            # no serial: fill with zeros or fake data
            self.dists[:] = 0.0
            return
        raw = self.ser.read(200).hex()
        for i, aid in enumerate(self.anchor_ids):
            idx = raw.find(aid)
            if idx >= 0:
                # extract ToF hex, swap endian, convert to distance in cm then to m
                hex_dis = raw[idx+16 : idx+24]
                try:
                    dis_cm = int.from_bytes(bytes.fromhex(hex_dis)[::-1], 'big')
                except ValueError:
                    dis_cm = 0
                if dis_cm >= 32768:
                    dis_cm = 0
                self.dists[i] = dis_cm / 100.0

    def compute_3d(self):
        """Compute (x,y,z) by least squares from m>=4 anchors"""
        P = self.anchors      # (m,3)
        R = self.dists        # (m,)
        # use anchor 0 as reference
        A, b = [], []
        x0, y0, z0 = P[0]
        r0 = R[0]
        for i in range(1, len(P)):
            xi, yi, zi = P[i]
            ri = R[i]
            A.append([2*(xi - x0), 2*(yi - y0), 2*(zi - z0)])
            b.append((r0**2 - ri**2)
                   + (xi**2 - x0**2)
                   + (yi**2 - y0**2)
                   + (zi**2 - z0**2))
        A = np.vstack(A)
        b = np.array(b)
        p_rel, *_ = np.linalg.lstsq(A, b, rcond=None)
        # if anchor0 is origin, p_rel is global; otherwise add P[0]
        return tuple(p_rel + P[0])

def main():
    # define anchors
    anchor_IDs = [
        '0241000000000000',
        '0341000000000000',
        '0441000000000000',
        '0541000000000000'
    ]
    anchor_positions = [
        (0.00,  0.00, 1.00),  # anchor6
        (5.00,  0.00, 1.00),  # anchor7
        (5.00, 10.00, 1.00),  # anchor8
        (0.00, 10.00, 1.00)   # anchor9
    ]

    # initialize
    uwb = UWB3DLocal(anchor_IDs, anchor_positions, port='/dev/ttyUSB0', baud=57600)

    # measurement loop
    N = 10  # number of measurements
    results = []
    for i in range(N):
        uwb.UWB_read()
        x, y, z = uwb.compute_3d()
        # record distances and computed coordinates
        results.append(list(uwb.dists) + [x, y, z])

    # prepare output directory
    output_dir = "/home/e520/uwb_results"
    os.makedirs(output_dir, exist_ok=True)

    # create DataFrame
    cols = anchor_IDs + ['tag_x','tag_y','tag_z']
    df = pd.DataFrame(results, columns=cols)

    # save CSV for MATLAB
    csv_path = os.path.join(output_dir, "uwb3d_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"CSV saved to {csv_path}")

    # save Excel for reporting
    excel_path = os.path.join(output_dir, "UWB_3d.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Excel saved to {excel_path}")

if __name__ == '__main__':
    main()

