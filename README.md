Run Space Ranger's registration algorithm to get 10x cellular barcodes corresponding to a spot, then segment cells in each spot using Stardist. For Visium OCT and FFPE the slide with 4 images is split equally into 4 separate files. This can be buggy if the total width is not consistent between files. Use shift parameter (in pixels) to fix this issue. Visium Cytassist works with full microscopy image and visium captured image.

To run Visium OCT or FFPE with 4 images in microscopy slide (eg. SVS format)
```
nextflow run main.nf \
--slide visium_slides/V13M13-279.svs \ # Slide containing 4 capture areas
--outdir output/V13M13-279 # Write output
-c nextflow.config
```

To run Visium OCT or FFPE with 4 images in microscopy slide (eg. SVS format) and to shift the start point (in pixels of the crop from the left and to specify the output directory name for each slide

```
nextflow run main.nf \
--slide 1-25-2022_JhaVisium2.svs \
--outdir output/JHAVisium2 \
--shift 3000 \
--imagenames 'SAME09_IBDUC147_0_v1 SAME09_IBDUC144_0_v1 SAME09_IBDUC142_0_v1 SAME09_NV196_0_v1'
```

To run Visium OCT or FFPE with just one image in microscopy slide (eg. ndpi format)
```
nextflow run main_nosplit_ds_microscopy.nf \
--visium_microscopy_slide a_15_Frozen.ndpi \ # Slide containing just one sample
--outdir output/a_15_Frozen # Write output
-c nextflow_cytassist.config
```

To run Visium OCT or FFPE with just one image in DOWNSAMPLED from microscopy slide (in JPEG format)
```

```




