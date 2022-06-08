# PGraph
python graph software for Rayleigh spectra

# Install Libraries
This program needs libraries below  
numpy 1.22.3  
pandas 1.4.2  
matplotlib 3.5.2  
tkinterdnd2 0.3.0  
`pip install numpy pandas matplotlib tkinterdnd2`  

# How to Use
## Load
In the same directory as pgraph.py  
`python pgraph.py`  
and this window appears.  
![image](https://user-images.githubusercontent.com/92524649/172366440-e29d69ff-916e-44b8-8e41-3e5f6e87b84f.png)  
Drag and drop files you want to draw.  
You can change x-axis labels (Wavelength or Energy).  
You can change y-axis labels (Intensity or Counts).  
## Change color and y-shift
To change graph color, set color and choose files you want to, then push 適用.
![image](https://user-images.githubusercontent.com/92524649/172367438-d237748a-ebfe-465a-97c6-d533da84cde1.png)  
As the same way, you can shift the graph along with y axis direction.
# Fitting
If you want to execute Lorentzian-fit, set initial params and push Fit.  
If you want to check the result on the graph area, check 結果を描画.
![image](https://user-images.githubusercontent.com/92524649/172368186-b4edbcf6-a392-4277-b7f2-1b3c3af3fcee.png)  
You can save the parameters.  
You can also load the parameters if there is a parameter file.
