'''Predator-prey simulation. Foxes and mice.

Version 4.0, last updated in January 2025.
'''
from argparse import ArgumentParser
import numpy as np
import random
import time

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
        
        # Arrays for mice and fox densities
        ms = np.zeros((hh, wh), float)
        fs = np.zeros((hh, wh), float)

        # Read initial animal data from file (with halo padding)
        row = 1
        for line in f.readlines():
            if line.strip():  # skip blank lines
                values = [int(i) for i in line.strip().split()]
                ms[row] = [0] + [v // 10 for v in values] + [0]
                fs[row] = [0] + [v  % 10 for v in values] + [0]
                row += 1

    # Initialize landscape
    lscape = np.zeros((hh, wh), int)
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
    neibs = np.zeros((hh, wh), int)
    for x in range(1, h+1):
        for y in range(1, w+1):
            neibs[x, y] = (lscape[x-1, y] + lscape[x+1, y] +
                           lscape[x, y-1] + lscape[x, y+1])

    # Arrays for next timestep and for PPM color outputs
    ms_nu = ms.copy()
    fs_nu = fs.copy()
    mcols = np.zeros((h, w), int)
    fcols = np.zeros((h, w), int)

    # Compute initial averages
    if nlands != 0:
        am = np.sum(ms) / nlands
        af = np.sum(fs) / nlands
    else:
        am = 0
        af = 0

    # Write initial header for the averages CSV
    with open("averages.csv", "w") as f_out:
        f_out.write("Timestep,Time,Mice,Foxes\n")

    # ---------------------------------------
    #  Performance improvement #2: Vectorized Updates
    # ---------------------------------------
    
    # We still keep the land_cells list from refactor_1 for consistency
    # (though we won't iterate over it in the update loop).
    land_cells = []
    for x in range(1, h+1):
        for y in range(1, w+1):
            if lscape[x, y] == 1:
                land_cells.append((x, y))

    # Create a Boolean mask for land to handle updates in vector form
    land_mask = (lscape == 1)

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

            with open("averages.csv", "a") as f_out:
                f_out.write("{},{:.1f},{:.17f},{:.17f}\n".format(i, i * dt, am, af))

            # Generate PPM map
            for x in range(1, h+1):
                for y in range(1, w+1):
                    if lscape[x, y]:
                        mcol = (ms[x, y] / mm) * 255 if mm != 0 else 0
                        fcol = (fs[x, y] / mf) * 255 if mf != 0 else 0
                        mcols[x-1, y-1] = mcol
                        fcols[x-1, y-1] = fcol

            with open("map_{:04d}.ppm".format(i), "w") as f_out:
                hdr = "P3\n{} {}\n{}\n".format(w, h, 255)
                f_out.write(hdr)
                for x in range(h):
                    for y in range(w):
                        if lscape[x+1, y+1]:
                            f_out.write("{} {} {}\n".format(fcols[x, y], mcols[x, y], 0))
                        else:
                            f_out.write("0 200 255\n")

        # -----------------------------
        # Vectorized neighbor summation
        # -----------------------------
        # Instead of np.roll (which would wrap edges), we directly sum neighbors:
        ms_neighbors = np.zeros_like(ms)
        fs_neighbors = np.zeros_like(fs)

        # For the region [1..h, 1..w] in ms, sum the top/bottom/left/right
        # These slices align with the halo. They do NOT wrap around, so
        # boundary indices remain zero (like the original code).
        ms_neighbors[1:h+1, 1:w+1] = (
            ms[0:h,   1:w+1] +
            ms[2:h+2, 1:w+1] +
            ms[1:h+1, 0:w]   +
            ms[1:h+1, 2:w+2]
        )
        fs_neighbors[1:h+1, 1:w+1] = (
            fs[0:h,   1:w+1] +
            fs[2:h+2, 1:w+1] +
            fs[1:h+1, 0:w]   +
            fs[1:h+1, 2:w+2]
        )

        # -----------------------------
        # Vectorized update equations
        # -----------------------------
        # These correspond exactly to:
        #   ms_nu[x,y] = ms[x,y] + dt*(r*ms[x,y] - a*ms[x,y]*fs[x,y] +
        #                             k*((sum_of_ms_neighbors) - neibs[x,y]*ms[x,y]))
        #
        # but done in a single array operation, restricted to land cells.
        ms_update = (r * ms) - (a * ms * fs) + k * (ms_neighbors - (neibs * ms))
        fs_update = (b * ms * fs) - (m * fs) + l * (fs_neighbors - (neibs * fs))

        ms_nu = ms + dt * ms_update
        fs_nu = fs + dt * fs_update

        # Clamp negative values to zero
        ms_nu[ms_nu < 0] = 0
        fs_nu[fs_nu < 0] = 0

        # Force water cells to remain zero (same as original loop logic)
        # i.e., do not let them accumulate animals.
        ms_nu[~land_mask] = 0
        fs_nu[~land_mask] = 0

        # Swap references for next iteration (avoids new array allocation each time)
        ms, ms_nu = ms_nu, ms
        fs, fs_nu = fs_nu, fs

if __name__ == "__main__":
    simCommLineIntf()
