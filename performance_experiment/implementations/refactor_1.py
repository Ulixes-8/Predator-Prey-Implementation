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
    par=ArgumentParser()
    par.add_argument("-r","--birth-mice",type=float,default=0.1,help="Birth rate of mice")
    par.add_argument("-a","--death-mice",type=float,default=0.05,help="Rate at which foxes eat mice")
    par.add_argument("-k","--diffusion-mice",type=float,default=0.2,help="Diffusion rate of mice")
    par.add_argument("-b","--birth-foxes",type=float,default=0.03,help="Birth rate of foxes")
    par.add_argument("-m","--death-foxes",type=float,default=0.09,help="Rate at which foxes starve")
    par.add_argument("-l","--diffusion-foxes",type=float,default=0.2,help="Diffusion rate of foxes")
    par.add_argument("-dt","--delta-t",type=float,default=0.5,help="Time step size")
    par.add_argument("-t","--time_step",type=int,default=10,help="Number of time steps at which to output files")
    par.add_argument("-d","--duration",type=int,default=500,help="Time to run the simulation (in timesteps)")
    par.add_argument("-ls","--landscape-seed",type=int,default=1,help="Random seed for initialising landscape")
    par.add_argument("-lp","--landscape-prop",type=float,default=0.75,help="Average proportion of landscape that will initially be land")
    par.add_argument("-lsm", "--landscape-smooth",type=int,default=2,help="Number of smoothing passes after landscape initialisation")
    par.add_argument("-f","--landscape-file",type=str,required=True,
                        help="Input landscape file")
    args=par.parse_args()
    sim(args.birth_mice,args.death_mice,args.diffusion_mice,args.birth_foxes,args.death_foxes,args.diffusion_foxes,args.delta_t,args.time_step,args.duration,args.landscape_file,args.landscape_seed,args.landscape_prop,args.landscape_smooth)

def sim(r,a,k,b,m,l,dt,t,d,lfile,lseed,lp,lsm):
    print("Predator-prey simulation",getVersion())
    with open(lfile,"r") as f:
        w,h=[int(i) for i in f.readline().split(" ")]
        print("Width: {} Height: {}".format(w,h))
        wh=w+2 # Width including halo
        hh=h+2 # Height including halo
        ms=np.zeros((hh,wh),float)
        fs=np.zeros((hh,wh),float)
        row=1
        for line in f.readlines():
            if line.strip():  # Skip blank lines
                values = [int(i) for i in line.strip().split()]
                # Read animals into array,padding with halo values.
                ms[row]=[0]+[i//10 for i in values]+[0]
                fs[row]=[0]+[i%10 for i in values]+[0]
                row += 1

    # Initialize landscape - MUST use the original random number generation to maintain identical results
    lscape=np.zeros((hh,wh),int)
    random.seed(lseed)
    for x in range(1,h+1):
        for y in range(1,w+1):
            prop = random.random()
            if prop <= lp:
                lscape[x,y] = 1
            else:
                lscape[x,y] = 0

    # Make landscape smoother - Using original algorithm for identical results
    for sm in range(lsm):
        for i in range(1,h+1):
            for j in range(1,w+1):
                if lscape[i,j] + lscape[i - 1,j] + lscape[i + 1,j] + lscape[i,j - 1] + lscape[i,j + 1] < 2:
                    lscape[i,j] = 0
                if lscape[i,j] + lscape[i - 1,j] + lscape[i + 1,j] + lscape[i,j - 1] + lscape[i,j + 1] > 2:
                    lscape[i,j] = 1

    # Set animal densities to zero where there is water
    for i in range(hh):
        for j in range(wh):
            if lscape[i,j] == 0:
                ms[i,j] = 0
                fs[i,j] = 0

    nlands = np.count_nonzero(lscape)
    print("Number of land-only squares: {}".format(nlands))
    
    # Pre-calculate number of land neighbours of each land square
    neibs = np.zeros((hh, wh), int)
    for x in range(1, h+1):
        for y in range(1, w+1):
            neibs[x,y] = lscape[x-1,y] + lscape[x+1,y] + lscape[x,y-1] + lscape[x,y+1]

    # Create copies of initial maps and arrays for PPM file maps
    ms_nu = ms.copy()
    fs_nu = fs.copy()
    mcols = np.zeros((h,w), int)
    fcols = np.zeros((h,w), int)
    
    # Calculate initial averages
    if nlands != 0:
        am = np.sum(ms) / nlands
        af = np.sum(fs) / nlands
    else:
        am = 0
        af = 0
    # print("Averages. Timestep: {} Time (s): {:.1f} Mice: {:.17f} Foxes: {:.17f}".format(0,0,am,af))
    
    # Write initial averages to CSV
    with open("averages.csv","w") as f:
        hdr = "Timestep,Time,Mice,Foxes\n"
        f.write(hdr)
    
    # Performance improvement: Pre-calculate land cell coordinates for faster processing
    land_cells = []
    for x in range(1, h+1):
        for y in range(1, w+1):
            if lscape[x, y] == 1:
                land_cells.append((x, y))
    
    # Calculate total timesteps
    tot_ts = int(d / dt)
    
    for i in range(0, tot_ts):
        # Output timestep data if needed
        if not i % t:
            mm = np.max(ms)
            mf = np.max(fs)
            if nlands != 0:
                am = np.sum(ms) / nlands
                af = np.sum(fs) / nlands
            else:
                am = 0
                af = 0
            # print("Averages. Timestep: {} Time (s): {:.1f} Mice: {:.17f} Foxes: {:.17f}".format(i,i*dt,am,af))
            
            # Write averages to CSV
            with open("averages.csv", "a") as f:
                f.write("{},{:.1f},{:.17f},{:.17f}\n".format(i,i*dt,am,af))
            
            # Prepare PPM image data
            for x in range(1, h+1):
                for y in range(1, w+1):
                    if lscape[x,y]:
                        if mm != 0:
                            mcol = (ms[x,y] / mm) * 255
                        else:
                            mcol = 0
                        if mf != 0:
                            fcol = (fs[x,y] / mf) * 255
                        else:
                            fcol = 0
                        mcols[x-1, y-1] = mcol
                        fcols[x-1, y-1] = fcol
            
            # Write PPM image
            with open("map_{:04d}.ppm".format(i), "w") as f:
                hdr = "P3\n{} {}\n{}\n".format(w, h, 255)
                f.write(hdr)
                for x in range(0, h):
                    for y in range(0, w):
                        if lscape[x+1, y+1]:
                            f.write("{} {} {}\n".format(fcols[x,y], mcols[x,y], 0))
                        else:
                            f.write("{} {} {}\n".format(0, 200, 255))
        
        # Performance improvement: Process only land cells using pre-calculated list
        for x, y in land_cells:
            # Cache common terms to avoid repeated calculations
            ms_xy = ms[x,y]
            fs_xy = fs[x,y]
            ms_neighbors = ms[x-1,y] + ms[x+1,y] + ms[x,y-1] + ms[x,y+1]
            fs_neighbors = fs[x-1,y] + fs[x+1,y] + fs[x,y-1] + fs[x,y+1]
            neighbor_count = neibs[x,y]
            
            # Update mice population
            ms_nu[x,y] = ms_xy + dt * ((r * ms_xy) - (a * ms_xy * fs_xy) + k * (ms_neighbors - (neighbor_count * ms_xy)))
            if ms_nu[x,y] < 0:
                ms_nu[x,y] = 0
            
            # Update foxes population
            fs_nu[x,y] = fs_xy + dt * ((b * ms_xy * fs_xy) - (m * fs_xy) + l * (fs_neighbors - (neighbor_count * fs_xy)))
            if fs_nu[x,y] < 0:
                fs_nu[x,y] = 0
        
        # Swap arrays for next iteration
        tmp = ms
        ms = ms_nu
        ms_nu = tmp
        tmp = fs
        fs = fs_nu
        fs_nu = tmp
        
if __name__ == "__main__":
    simCommLineIntf()