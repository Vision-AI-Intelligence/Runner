model_dir=./efficientdet_d0_coco17_tpu-32/custom
out_dir=$model_dir/exported_model
mkdir -p $out_dir

python exporter_main_v2.py \
    --input_type="image_tensor" \
    --pipeline_config_path=$model_dir/pipeline.config \
    --trained_checkpoint_dir=$model_dir/ \
    --output_directory=$out_dir
