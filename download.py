import ee
from geetools import batch
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

def download_NAIP_toLocal(bbox, savefolder, scale=1):
    """
    downloads NAIP imagery from the specified bounding box
    """
    AOI = ee.Geometry.Rectangle(list(bbox), "EPSG:4326", False)

    collection = (
        ee.ImageCollection("USDA/NAIP/DOQQ")
        .filterDate("2018-01-01", "2019-01-01")
        .filterBounds(AOI)
        .select(['R', 'G', 'B', 'N'])
    )

    image = ee.Image(collection.mosaic()).clip(AOI)
    batch.image.toLocal(image, savefolder, scale=scale, region=AOI)
    
def stack_bands(name, outname):
    file_list = [name + '.R.tif', name + '.G.tif', name + '.B.tif', name + '.N.tif']

    # Read metadata of first file
    with rasterio.open(file_list[0]) as src0:
        meta = src0.meta

    # Update meta to reflect the number of layers
    meta.update(count = len(file_list))

    # Read each layer and write it to stack
    with rasterio.open(outname, 'w', **meta) as dst:
        for id, layer in enumerate(file_list, start=1):
            with rasterio.open(layer) as src1:
                dst.write_band(id, src1.read(1))

def download_naip(bbox,savefolder,savefilename):
    download_NAIP_toLocal(bbox, savefolder, scale=1)
    stack_bands(savefolder +'/download',savefilename)

# Initialize the Earth Engine module.
ee.Initialize()

# Coordinates of the boundary of the region to download
# Can copy and paste from http://bboxfinder.com/

# bbox = [lon[0], lat[0], lon[1], lat[1]]
bbox = [-78.944538,35.995766,-78.931020,36.006078]

# Where to save the files
savefolder = 'naipdownload'
savefilename = "stacked_naip_sample.tif"

# Download the image
download_naip(bbox,savefolder,savefilename)