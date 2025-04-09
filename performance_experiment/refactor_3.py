"""
Predator-prey simulation. Foxes and mice.

Version 4.0, last updated in January 2025.
(This version defers all writes and preserves bit-for-bit output.)
"""

from argparse import ArgumentParser
import numpy as np
import random
import time

from numba import njit, prange

def getVersion():
    return 4.0

def simCommLineIntf():
    par = ArgumentParser()
    par.add_argument("-r", "--birth-mice",       type=float, default=0.1, help="Birth rate of mice")
    par.add_argument("-a", "--death-mice",       type=float, default=0.05, help="Rate at which foxes eat mice")
    par.add_argument("-k", "--diffusion-mice",   type=float, default=0.2,  help="Diffusion rate of mice")
    par.add_argument("-b", "--birth-foxes",      type=float, default=0.03, help="Birth rate of foxes")
    par.add_argument("-m", "--death-foxes",      type=float, default=0.09, help="Rate at which foxes starve")
    par.add_argument("-l", "--diffusion-foxes",  type=float, default=0.2,  help="Diffusion rate of foxes")
    par.add_argument("-dt","--delta-t",          type=float, default=0.5,  help="Time step size")
    par.add_argument("-t", "--time_step",        type=int,   default=10,   help="Number of time steps at which to output files")
    par.add_argument("-d", "--duration",         type=int,   default=500,  help="Time to run the simulation (in timesteps)")
    par.add_argument("-ls","--landscape-seed",   type=int,   default=1,    help="Random seed for initialising landscape")
    par.add_argument("-lp","--landscape-prop",   type=float, default=0.75, help="Average proportion of landscape that will initially be land")
    par.add_argument("-lsm","--landscape-smooth",type=int,   default=2,    help="Number of smoothing passes after landscape initialisation")
    par.add_argument("-f", "--landscape-file",   type=str, required=True,
                    help="Input landscape file")
    args = par.parse_args()
    sim(args.birth_mice, args.death_mice, args.diffusion_mice,
        args.birth_foxes, args.death_foxes, args.diffusion_foxes,
        args.delta_t, args.time_step, args.duration, args.landscape_file,
        args.landscape_seed, args.landscape_prop, args.landscape_smooth)

def sim(r, a, k, b, m, l, dt, t, d, lfile, lseed, lp, lsm):
    print("Predator-prey simulation", getVersion())
    with open(lfile, "r") as f:
        w, h = [int(i) for i in f.readline().split()]
        print("Width: {} Height: {}".format(w, h))
        wh = w + 2  # Width including halo
        hh = h + 2  # Height including halo
        
        # Arrays for mice and fox densities (double precision)
        ms = np.zeros((hh, wh), dtype=np.float64)
        fs = np.zeros((hh, wh), dtype=np.float64)

        # Read initial animal data from file (with halo padding)
        row = 1
        for line in f.readlines():
            if line.strip():  # skip blank lines
                values = [int(i) for i in line.strip().split()]
                ms[row] = [0] + [v // 10 for v in values] + [0]
                fs[row] = [0] + [v  % 10 for v in values] + [0]
                row += 1

    # Initialize landscape (int32 for clarity under Numba)
    lscape = np.zeros((hh, wh), dtype=np.int32)
    random.seed(lseed)
    for x in range(1, h+1):
        for y in range(1, w+1):
            if random.random() <= lp:
                lscape[x, y] = 1
            else:
                lscape[x, y] = 0

    # Smooth the landscape
    for _ in range(lsm):
        for i in range(1, h+1):
            for j in range(1, w+1):
                nbr_sum = (lscape[i, j] +
                           lscape[i-1, j] + lscape[i+1, j] +
                           lscape[i, j-1] + lscape[i, j+1])
                if nbr_sum < 2:
                    lscape[i, j] = 0
                if nbr_sum > 2:
                    lscape[i, j] = 1

    # Zero out animals where there's water
    for i in range(hh):
        for j in range(wh):
            if lscape[i, j] == 0:
                ms[i, j] = 0
                fs[i, j] = 0

    nlands = np.count_nonzero(lscape)
    print("Number of land-only squares: {}".format(nlands))

    # Pre-calculate number of land neighbors (for diffusion)
    neibs = np.zeros((hh, wh), dtype=np.int32)
    for x in range(1, h+1):
        for y in range(1, w+1):
            neibs[x, y] = (lscape[x-1, y] + lscape[x+1, y] +
                           lscape[x, y-1] + lscape[x, y+1])

    # Arrays for next timestep (reused each iteration)
    ms_nu = np.zeros_like(ms, dtype=np.float64)
    fs_nu = np.zeros_like(fs, dtype=np.float64)

    # Arrays for PPM color outputs
    mcols = np.zeros((h, w), dtype=np.int32)
    fcols = np.zeros((h, w), dtype=np.int32)

    # ------------------------------
    #  DEFERRED I/O: storing in mem
    # ------------------------------
    csv_lines = ["Timestep,Time,Mice,Foxes\n"]  # CSV header
    ppm_files = []  # list of (filename, content)

    # Compute initial averages
    if nlands != 0:
        am = np.sum(ms) / nlands
        af = np.sum(fs) / nlands
    else:
        am = 0
        af = 0

    # Total timesteps
    tot_ts = int(d / dt)

    for i in range(tot_ts):
        
        # Output data every 't' steps
        if i % t == 0:
            mm = np.max(ms)
            mf = np.max(fs)
            if nlands != 0:
                am = np.sum(ms) / nlands
                af = np.sum(fs) / nlands
            else:
                am = 0
                af = 0

            # Build CSV line for this timestep
            csv_lines.append(f"{i},{i*dt:.1f},{am:.17f},{af:.17f}\n")

            # Build PPM data in memory
            for x_ in range(1, h+1):
                for y_ in range(1, w+1):
                    if lscape[x_, y_]:
                        mcol = (ms[x_, y_] / mm) * 255 if mm != 0 else 0
                        fcol = (fs[x_, y_] / mf) * 255 if mf != 0 else 0
                        mcols[x_-1, y_-1] = int(mcol)
                        fcols[x_-1, y_-1] = int(fcol)
                    # else: water => we do nothing, handled in the final text

            filename = f"map_{i:04d}.ppm"
            lines = []
            # PPM header
            lines.append(f"P3\n{w} {h}\n255\n")
            # Each pixel
            for row_ in range(h):
                for col_ in range(w):
                    if lscape[row_+1, col_+1]:
                        lines.append(f"{fcols[row_, col_]} {mcols[row_, col_]} 0\n")
                    else:
                        lines.append("0 200 255\n")

            ppm_text = "".join(lines)
            ppm_files.append((filename, ppm_text))

        # -----------------------------------------------------
        # Single-pass neighbor summation + update (in-place)
        # -----------------------------------------------------
        ms_nu.fill(0)
        fs_nu.fill(0)

        update_arrays_parallel_inplace(ms, fs, ms_nu, fs_nu, neibs, dt,
                                       r, a, k, b, m, l, (lscape == 1))

        # Swap references for next iteration
        ms, ms_nu = ms_nu, ms
        fs, fs_nu = fs_nu, fs

    # -----------------------------------------
    # After the loop: write out CSV and PPMs
    # -----------------------------------------
    with open("averages.csv", "w") as f_out:
        f_out.writelines(csv_lines)

    for fname, ppm_text in ppm_files:
        with open(fname, "w") as f_out:
            f_out.write(ppm_text)

@njit(parallel=True)
def update_arrays_parallel_inplace(ms, fs, ms_nu, fs_nu, neibs, dt,
                                   r, a, k, b, m, l, land_mask):
    """
    Single-pass approach:
     - For each cell in [1..hh-2, 1..wh-2], if it's land, compute neighbor sums
       and update ms_nu[i,j], fs_nu[i,j].
    """
    hh, wh = ms.shape

    for i in prange(1, hh-1):  # outer loop parallel
        for j in range(1, wh-1):
            if land_mask[i, j]:
                ms_xy = ms[i, j]
                fs_xy = fs[i, j]
                sum_m = ms[i-1, j] + ms[i+1, j] + ms[i, j-1] + ms[i, j+1]
                sum_f = fs[i-1, j] + fs[i+1, j] + fs[i, j-1] + fs[i, j+1]
                nb_count = neibs[i, j]

                # dM/dt
                ms_up = (r * ms_xy) - (a * ms_xy * fs_xy) \
                        + k * (sum_m - nb_count * ms_xy)
                # dF/dt
                fs_up = (b * ms_xy * fs_xy) - (m * fs_xy) \
                        + l * (sum_f - nb_count * fs_xy)

                new_ms = ms_xy + dt * ms_up
                new_fs = fs_xy + dt * fs_up

                if new_ms < 0:
                    new_ms = 0
                if new_fs < 0:
                    new_fs = 0

                ms_nu[i, j] = new_ms
                fs_nu[i, j] = new_fs
            else:
                ms_nu[i, j] = 0
                fs_nu[i, j] = 0

if __name__ == "__main__":
    simCommLineIntf()
