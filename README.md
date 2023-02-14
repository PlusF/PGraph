# PGraph
python graph software for Rayleigh, Raman, Absorbance spectra

# Install Libraries
`pip install -r requirements.txt`  

# How to Use
## Load
move to the directory where `pgraph.py` is placed.
Then type
`python pgraph.py`  
and this window shows up.  
![image](https://user-images.githubusercontent.com/92524649/172366440-e29d69ff-916e-44b8-8e41-3e5f6e87b84f.png)  
Drag and drop files which contains spectrum data.  
You can change x-axis labels (Wavelength or Energy).  
You can change y-axis labels (Intensity or Counts).  
## Change color and y-shift
To change graph color, set color and choose files you want to, then push 適用.
![image](https://user-images.githubusercontent.com/92524649/172367438-d237748a-ebfe-465a-97c6-d533da84cde1.png)  
As the same way, you can shift the graph along y axis direction.
# Fitting
If you want to fit, set initial params and push Fit.
You can choose from Lorentzian, Gaussian and Voigt.
If you want to check the result on the graph area, check 結果を描画.
![image](https://user-images.githubusercontent.com/92524649/172368186-b4edbcf6-a392-4277-b7f2-1b3c3af3fcee.png)  
You can save/load the parameters.
