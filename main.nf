/* 
 * pipeline input parameters 
 */

params.slide = "$baseDir/test/3-11-2022_Visium_Slide1_Raphael.svs"
params.invocation = "$baseDir/bin/_invocation"
params.outdir = "$baseDir/test/out"

log.info """\
         S E G M E N T A T I O N   P I P E L I N E    
         ===========================================
         slide        : ${params.slide}
         outdir       : ${params.outdir}
         """
         .stripIndent()

slide = file(params.slide)

process split_images {
  module  "python/3.8.2: openslide"

  input:
  path slide from params.slide

  output:
  path "*.jpg" into jpeg_ch

  script:
  """
  $baseDir/bin/split_visium.py \
  $slide 
  """
}

process run_spaceranger_image {
  publishDir "$params.outdir/${jpeg.getSimpleName()}", mode: 'copy', overwrite: true

  module  "spaceranger/1.3.1" 
 
  input:
  path jpeg from jpeg_ch.flatten() 
  path invocation from params.invocation

  output:
  tuple \
      path(jpeg), \
      path("output/outs/image_scalefactors.json"), \
      path("output/outs/tissue_positions_list.csv") \
      into spaceranger_ch

  script:
  """
  IMAGE=\$(readlink -f $jpeg)
  sed "s|<ADD_IMAGE>|\$IMAGE|g" $invocation > _input
  spaceranger mrp _input output
  """
}

process run_segmentation {
  publishDir "$params.outdir/${jpeg.getSimpleName()}", mode: 'copy', overwrite: true

  input:
  tuple \
    path(jpeg), \
    path(scalefactors), \
    path(positions) \
    from spaceranger_ch

  output:
  path "stardist_detections.csv"

  script:
  """
  $baseDir/bin/segment_visium.py $jpeg $scalefactors $positions
  """
}

/*
workflow {
  split_images | 
}
*/
