import meep as mp
import numpy as np
import matplotlib.pyplot as plt

# === Define parameters ===
resolution = 100  # pixels/μm
wavelength = 0.8  # μm (800 nm)
frequency = 1 / wavelength
fwidth = 0.4  # Frequency width for Gaussian source

# Layer thicknesses (all in μm)
t_silicon = 0.05  # 50 nm
t_sio2 = 0.05
t_total = t_silicon * 2 + t_sio2

# Size of simulation cell
dpml = 1.0
sx = 0
sy = 0
sz = dpml + t_total + 2 + dpml  # padding + layers + air + pml
cell_size = mp.Vector3(0, 0, sz)

# === Define materials ===
# You can replace this with more complex materials or dispersive models
silicon = mp.Medium(index=3.45)
sio2 = mp.Medium(index=1.45)
air = mp.Medium(index=1.0)

# === Geometry ===
geometry = [
    mp.Block(size=mp.Vector3(mp.inf, mp.inf, t_silicon),
             center=mp.Vector3(z=0.5*t_total - t_silicon/2),
             material=silicon),
    
    mp.Block(size=mp.Vector3(mp.inf, mp.inf, t_sio2),
             center=mp.Vector3(z=0),
             material=sio2),

    mp.Block(size=mp.Vector3(mp.inf, mp.inf, t_silicon),
             center=mp.Vector3(z=-0.5*t_total + t_silicon/2),
             material=silicon)
]

# === Source ===
sources = [mp.Source(mp.GaussianSource(frequency, fwidth=fwidth),
                     component=mp.Ez,
                     center=mp.Vector3(z=0.5 * sz - dpml - 0.5),
                     size=mp.Vector3())]

# === Boundary conditions ===
pml_layers = [mp.PML(dpml)]

# === Simulation ===
sim = mp.Simulation(cell_size=cell_size,
                    boundary_layers=pml_layers,
                    geometry=geometry,
                    sources=sources,
                    resolution=resolution)

# === Set up flux regions ===
# Reflection monitor (above sample)
refl_fr = mp.FluxRegion(center=mp.Vector3(z=0.5 * sz - dpml - 0.8), size=mp.Vector3())
refl = sim.add_flux(frequency, fwidth, 100, refl_fr)

# === Run simulation to get reflection ===
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(z=0), 1e-9))

# === Get reflected flux ===
refl_flux = mp.get_fluxes(refl)[0]
print("Reflected flux:", refl_flux)

# === Save flux spectrum if needed ===
freqs = mp.get_flux_freqs(refl)
plt.plot(1 / np.array(freqs), mp.get_fluxes(refl))  # Plot vs wavelength
plt.xlabel("Wavelength (μm)")
plt.ylabel("Reflected power")
plt.show()