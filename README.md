# Neo-Bed-Flattening
A script and a HTML I made for my Orca FullSpectrum Fork in HTMLand Python. Basically reads the bed_mesh from Klipper and makes an inverted STL that you need to print with high resolution layer.

Been toying yesterday with this idea. A easy to print system that would compensate for the bed imperfections

Of course is a first day idea and first results, so more tests to come

First photo is my U1 as it is bed mesh, pretty ok, but, why stop there?

2nd photo. Is a printed bed mesh in reverse with a 0.4 height and 0.05 layers (U1 actually can print if you set the width lines a bit larger and dont mind about perimeters if going fast.

Gyroid was a bad idea, but a decent second print (first was triangular but because double path cross the precision is lower)

3rd Photo. And finally first result. Overall bed is better, but the import is the fine print. Most of the bed has a 0.05 error! Thats SUPER flat

Notes for users.
- I will upload an HTML & Python to make the stl
- I dont rememed a thicknes higher than 0.3, the magnets wont stick to the Metal PEI sheet
- More tests needed

- The easiest way is to use the STL inverted on X axis and ‘FLIP’ the PEI metal sheet, then you dont need to place it by hand

ENJOY THE Neo-FLATNESS!

# Neo-Bed-Flattening

**Neo-Bed-Flattening** is a specialized tool designed to solve 3D printer bed leveling issues once and for all. It generates a custom-fitted 3D printable "shim" or plate based on your Klipper `bed_mesh` data. 

By placing this precision-printed shim under your build surface (e.g., PEI sheet), you can physically compensate for bed plate irregularities, achieving a near-perfectly flat surface without relying solely on software-based mesh compensation.

## Key Features

- **Precision Compensation**: Uses Bicubic interpolation to upsample Klipper's sparse probed matrix for a smooth, high-fidelity surface.
- **Adjustable Base**: Customizable base plate thickness to fit your specific setup.
- **Smoothing Levels**: Control the mesh density for the generated STL file.
- **Inversion Support**: Toggle between Generating a matching surface or a corrective (inverse) surface for physical leveling.
- **Heatmap Visualization**: Real-time representation of your bed's height variance (Blue for low, Red for high).

## Available Versions

### 1. Web Application (Recommended)
A modern, interactive browser-based tool with a 3D engine.
- **How to use**: Just open `index.html` in any modern browser.
- **Features**: Drag-and-drop JSON loading, interactive 3D preview, real-time settings adjustment, and direct STL export.

### 2. Python CLI
A lightweight command-line script for automated workflows.
- **How to use**: 
  ```bash
  python3 compensator.py <bed_mesh.json> --output neo_bed_flattening.stl --base 0.5 --smoothing 2
  ```

## How It Works

1. **Export**: Get your `bed_mesh` data from Klipper (usually found in `printer.cfg` or exported as a JSON).
2. **Process**: Load the JSON into Neo-Bed-Flattening.
3. **Generate**: Adjust the base thickness (e.g., 0.5mm) and smoothing.
4. **Print**: Print the resulting STL in a heat-resistant material (like PETG or ASA).
5. **Level**: Place the shim under your magnetic sheet/PEI plate.
6. **Enjoy**: Revel in your perfectly flat first layers.

---
*Created by [sebsucmor-alt](https://github.com/sebsucmor-alt/)*

ADDED X/Y Flip.

The idea is to 'flip' the stl and printed mirroed, so you can just 'FLIP' the PEI-SHEET
