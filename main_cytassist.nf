/* 
 * pipeline input parameters 
 */

params.microscopy_slide = "$baseDir/cytassist_test/MAGA03_B10_257_1001.svs"
params.visium_slide = "$baseDir/cytassist_test/MAGA03_257-1001_0_cytassist.tif"
params.downsample_factor = 7 
params.invocation = "$baseDir/bin/_invocation_cytassist_nf"
params.outdir = "$baseDir/test/cytassist"

log.info """\
         S E G M E N T A T I O N   P I P E L I N E    
         ===========================================
         microscopy_slide : ${params.microscopy_slide}
         visium_slide : ${params.visium_slide}
         downsample_factor  : ${params.downsample_factor}
         spaceranger_config: ${params.invocation}
         outdir       : ${params.outdir}
         """
         .stripIndent()

//microscopy_slide = file(params.slide)

process downsample_image {
  
  input:
  path microscopy_slide from params.microscopy_slide
  val downsample_factor from params.downsample_factor

  output:
  path "*.jpg" into jpeg_ch

  script:
  """
  $baseDir/bin/downsample_visium_cytassist.py \
  $microscopy_slide \
  --downsample_factor $downsample_factor 
  """
}

process run_spaceranger_image {

  module  "spaceranger/2.0.0" 
 
  input:
  path visium_slide from params.visium_slide
  path jpeg from jpeg_ch.flatten() 
  path invocation from params.invocation
  path microscopy_slide from params.microscopy_slide
  val downsample_factor from params.downsample_factor

  output:
  tuple \
      path("output/outs/image_scalefactors.json"), \
      path("output/outs/tissue_positions.csv"), \
      path(microscopy_slide), \
      val(downsample_factor) \
      into spaceranger_ch

  script:
  """
  M_IMAGE=\$(readlink -f $jpeg)
  V_IMAGE=\$(readlink -f $visium_slide)

  sed -e "s|<M_IMAGE>|\$M_IMAGE|g" -e "s|<V_IMAGE>|\$V_IMAGE|g" $invocation > _input
  

  spaceranger mrp _input output
  """
}

process run_segmentation {
  publishDir "$params.outdir/${microscopy_slide.getSimpleName()}", mode: 'copy', overwrite: true

  input:
  tuple \
    path(scalefactors), \
    path(positions), \
    path(microscopy_slide), \
    val(downsample_factor) \
    from spaceranger_ch

  output:
  path "stardist_detections.csv"
  path "plots/*"

  script:
  """
  $baseDir/bin/segment_visium_cytassist.py $microscopy_slide $scalefactors $positions $downsample_factor
  """
}

/*
workflow {
  split_images | 
}
*/
